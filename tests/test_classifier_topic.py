import pytest
import torch
import pandas as pd
from factfinder import TextClassifierTopics

path_to_file = "data/raw/Адмиралтейский.csv"


@pytest.fixture
def test_data():
    df_predict = pd.read_csv(path_to_file, sep=";")
    df_predict.rename(columns={"Текст комментария": "Текст"}, inplace=True)
    df_predict = df_predict.dropna(subset=["Текст"])
    df_predict = df_predict.head(3)
    return df_predict


@pytest.fixture
def model():
    model = TextClassifierTopics(
        repository_id="Sandrro/text_to_subfunction_v10",
        number_of_categories=1,
        device_type=torch.device("cpu"),
    )
    return model


def test_init():
    # Arrange
    repository_id = "Sandrro/text_to_subfunction_v10"
    number_of_categories = 1
    device_type = torch.device("cpu")

    # Act
    classifier = TextClassifierTopics(
        repository_id, number_of_categories, device_type
    )

    # Assert
    assert classifier.REP_ID == repository_id
    assert classifier.CATS_NUM == number_of_categories
    assert classifier.classifier.model.name_or_path == repository_id
    assert (
        classifier.classifier.tokenizer.name_or_path
        == "cointegrated/rubert-tiny2"
    )


def test_cats_probs(model, test_data):
    expected_df = pd.DataFrame(
        {
            "cats": [
                "Вопросы граждан о проектах/планах/сроках/ходе проведения работ по благоустройству",
                "Не ЦУР",
                "Вопросы по оплате проезда в общественном транспорте",
            ],
            "probs": ["1.0", "0.999", "0.98"],
        }
    )

    test_data[["cats", "probs"]] = pd.DataFrame(
        test_data["Текст"].progress_map(lambda x: model.run(x)).to_list()
    )
    assert test_data["cats"].equals(expected_df["cats"])
    assert test_data["probs"].equals(expected_df["probs"])
