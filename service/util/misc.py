import os
from pathlib import Path
from typing import BinaryIO, List

from fastapi import HTTPException, Request, status
from fastapi.responses import StreamingResponse
from tqdm.auto import tqdm
from urllib.request import urlretrieve


class VideoNamePool:
    latest = -1

    @classmethod
    def init(cls):
        all_video_ids: List[int] = []
        for directory in filter(lambda x: os.path.isdir(os.path.join("data", x)), os.listdir("data")):
            try:
                all_video_ids.append(int(directory))
            except ValueError:
                continue

        if len(all_video_ids) > 0:
            cls.latest = max(all_video_ids)
        else:
            cls.latest = -1

    @classmethod
    def get(cls):
        cls.latest += 1
        return cls.latest


# https://github.com/tiangolo/fastapi/issues/1240
def send_bytes_range_requests(
    file_obj: BinaryIO, start: int, end: int, chunk_size: int = 10_000
):
    """Send a file in chunks using Range Requests specification RFC7233

    `start` and `end` parameters are inclusive due to specification
    """
    with file_obj as f:
        f.seek(start)
        pos = f.tell()
        while pos <= end:
            read_size = min(chunk_size, end + 1 - pos)
            yield f.read(read_size)


def _get_range_header(range_header: str, file_size: int) -> tuple[int, int]:
    def _invalid_range():
        return HTTPException(
            status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            detail=f"Invalid request range (Range:{range_header!r})",
        )

    try:
        h = range_header.replace("bytes=", "").split("-")
        start = int(h[0]) if h[0] != "" else 0
        end = int(h[1]) if h[1] != "" else file_size - 1
    except ValueError:
        raise _invalid_range()

    if start > end or start < 0 or end > file_size - 1:
        raise _invalid_range()
    return start, end


def range_requests_response(
    request: Request, file_path: str, content_type: str
):
    """Returns StreamingResponse using Range Requests of a given file"""

    file_size = os.stat(file_path).st_size
    range_header = request.headers.get("range")

    headers = {
        "content-type": content_type,
        "accept-ranges": "bytes",
        "content-encoding": "identity",
        "content-length": str(file_size),
        "access-control-expose-headers": (
            "content-type, accept-ranges, content-length, "
            "content-range, content-encoding"
        ),
    }
    start = 0
    end = file_size - 1
    status_code = status.HTTP_200_OK

    if range_header is not None:
        start, end = _get_range_header(range_header, file_size)
        size = end - start + 1
        headers["content-length"] = str(size)
        headers["content-range"] = f"bytes {start}-{end}/{file_size}"
        status_code = status.HTTP_206_PARTIAL_CONTENT

    return StreamingResponse(
        send_bytes_range_requests(open(file_path, mode="rb"), start, end),
        headers=headers,
        status_code=status_code,
    )


class DownloadProgressBar(tqdm):
    total: int

    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_file(url: str, file_path: str, progress_bar: bool = True) -> str:
    path = Path(file_path)
    path.parent.mkdir(exist_ok=True, parents=True)
    if not path.exists():
        if progress_bar:
            with DownloadProgressBar(unit="B", unit_scale=True, miniters=1, desc=f"Downloading {path.name}") as pb:
                urlretrieve(url, filename=path, reporthook=pb.update_to)
        else:
            urlretrieve(url, filename=path)

    return str(path)
