from basemodels import PredictionInput

def fake_model(inputs: PredictionInput):
    total = inputs.feature1 + inputs.feature2
    return f'predição para as features dadas: {total}'
