import dialogflow_v2 as dialogflow
import google.cloud.language

def analyze_intent(project_id, session_id, text: str, language_code, log):
    """Returns the result of detect intent with texts as inputs.

    Using the same `session_id` between requests allows continuation
    of the conversaion."""
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
    log.info('Session path: {}\n'.format(session))

    text_input = dialogflow.types.TextInput(
        text=text, language_code=language_code)

    query_input = dialogflow.types.QueryInput(text=text_input)

    response = session_client.detect_intent(
        session=session, query_input=query_input)

    return response.query_result


def analyze_categories(text: str, log) -> list:
    client = google.cloud.language.LanguageServiceClient()
    document = google.cloud.language.types.Document(
        content=text,
        type=google.cloud.language.enums.Document.Type.PLAIN_TEXT,
    )

    try:
        response = client.classify_text(
            document=document
        ).categories
    except Exception as ex:
        log.critical(ex)
        response = []

    return response


def analyze_sentiment(text: str, log) -> dict:
    client = google.cloud.language.LanguageServiceClient()
    document = google.cloud.language.types.Document(
        content=text,
        type=google.cloud.language.enums.Document.Type.PLAIN_TEXT,
    )

    try:
        sentiment = client.analyze_sentiment(
            document=document,
            encoding_type='UTF32',
        ).document_sentiment
    except Exception as ex:
        print(ex)
        sentiment = {
            'score': 0.0,
            'magnitude': 0.0
        }

    return sentiment
