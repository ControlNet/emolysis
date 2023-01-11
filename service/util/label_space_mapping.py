import numpy as np

# =============================================================================
# Emotion Mapping
# =============================================================================


def affectnet_to_main(emo_scores):
    emo_prob = np.zeros(9)
    emo_prob[0] = emo_scores[1] + emo_scores[3]  # fear (contempt + fear)
    emo_prob[1] = emo_scores[0]  # anger (anger)
    emo_prob[2] = emo_scores[4]  # joy (happy)
    emo_prob[3] = emo_scores[6]  # sadness (sad)
    emo_prob[4] = emo_scores[2]  # disgust (disgust)
    emo_prob[5] = emo_scores[7]  # surprise
    emo_prob[6] = 0.0  # trust
    emo_prob[7] = 0.0  # anticipation
    emo_prob[8] = emo_scores[5]  # none
    return emo_prob


def bold_to_main(emo_scores):
    emo_prob = np.zeros(9)
    emo_prob[0] = emo_scores[22] + emo_scores[23]  # fear (disquitement + fear)
    emo_prob[1] = emo_scores[18] + emo_scores[19]  # anger (annoyance +anger)
    emo_prob[2] = emo_scores[0] + emo_scores[1] + emo_scores[2] \
                  + emo_scores[4] + emo_scores[5] + emo_scores[6] + emo_scores[7] \
                  + emo_scores[10] + emo_scores[
                      15]  # joy (peace+affection+engagement+confidence+happy+pleasure+sympathy+yearning)
    emo_prob[3] = emo_scores[12] + emo_scores[13] + emo_scores[14] + emo_scores[20] \
                  + emo_scores[21] + emo_scores[24] + emo_scores[25]  # sadness
    emo_prob[4] = emo_scores[16] + emo_scores[17]  # disgust
    emo_prob[5] = emo_scores[8] + emo_scores[9] + emo_scores[11]  # surprise
    emo_prob[6] = 0.0  # trust
    emo_prob[7] = emo_scores[3]  # anticipation
    emo_prob[8] = 0.0  # none
    return emo_prob


def cped_to_main(emo_scores):
    emo_prob = np.zeros(9)
    emo_prob[0] = emo_scores[7] + emo_scores[11]  # fear
    emo_prob[1] = emo_scores[5]  # anger
    emo_prob[2] = emo_scores[0] + emo_scores[1] + emo_scores[2] \
                  + emo_scores[3]  # joy
    emo_prob[3] = emo_scores[6] + emo_scores[8] + emo_scores[12]  # sadness
    emo_prob[4] = emo_scores[9]  # disgust
    emo_prob[5] = emo_scores[10]  # surprise
    emo_prob[6] = 0.0  # trust
    emo_prob[7] = 0.0  # anticipation
    emo_prob[8] = emo_scores[4]  # none
    return emo_prob


# =============================================================================
# Valence Mapping
# =============================================================================

def translate(value, r1_Min, r1_Max, r2_Min, r2_Max):
    # Figure out how 'wide' each range is
    r1_Span = r1_Max - r1_Min
    r2_Span = r2_Max - r2_Min

    # Convert the r1 range into a 0-1 range (float)
    valueScaled = float(value - r1_Min) / float(r1_Span)

    # Convert the 0-1 range into a value in the r2 range.
    return r2_Min + (valueScaled * r2_Span)


def affectnet_to_main_valence(valence_score):
    try:
        affectnet_min = -1
        affectnet_max = 1

        main_min = 1
        main_max = 1000

        valence_mapped_main = translate(valence_score,
            affectnet_min, affectnet_max,
            main_min, main_max)
    except Exception:
        raise ValueError('The predicted valence score is not valid')
    return valence_mapped_main


def bold_to_main_valence(valence_score):
    try:
        bold_min = 1
        bold_max = 10

        main_min = 1
        main_max = 1000

        valence_mapped_main = translate(valence_score,
            bold_min, bold_max,
            main_min, main_max)
    except Exception:
        raise ValueError('The predicted valence score is not valid')
    return valence_mapped_main


# =============================================================================
# Arousal Mapping
# =============================================================================

def bold_to_main_arousal(arousal_score):
    try:
        bold_min = 1
        bold_max = 10

        main_min = 1
        main_max = 1000

        arousal_mapped_main = translate(arousal_score,
            bold_min, bold_max,
            main_min, main_max)
    except Exception:
        raise ValueError('The predicted arousal score is not valid')
    return arousal_mapped_main


def affectnet_to_main_arousal(arousal_score):
    try:
        affectnet_min = -1
        affectnet_max = 1

        main_min = 1
        main_max = 1000

        arousal_mapped_main = translate(arousal_score,
            affectnet_min, affectnet_max,
            main_min, main_max)
    except Exception:
        raise ValueError('The predicted arousal score is not valid')
    return arousal_mapped_main
