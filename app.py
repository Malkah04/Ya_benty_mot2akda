
import streamlit as st
import tempfile
from pathlib import Path

from workflow.workflow import process_source_question


st.set_page_config(
    page_title="3ala Damanty",
    layout="wide",
)

st.title("3ala Damanty")
st.caption("RAG Assistant")


if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "source" not in st.session_state:
    st.session_state.source = None

if "source_type" not in st.session_state:
    st.session_state.source_type = None


with st.sidebar:

    st.header("Knowledge Source")

    source_option = st.selectbox(
        "Choose source type",
        [
            "File",
            "Audio",
            "Web URL",
            "Wikipedia",
        ],
    )

    source = None
    uploaded_file = None
    source_type = None

    if source_option == "File":

        uploaded_file = st.file_uploader(
            "Upload your document",
            type=["pdf", "docx", "txt", "pptx"],
            key="document_uploader",
        )

        if uploaded_file is not None:
            source_type = "file"

            st.success("Document uploaded successfully!")

            st.caption(f"{uploaded_file.name}")

    elif source_option == "Audio":

        uploaded_file = st.file_uploader(
            "Upload your audio",
            type=["wav"],
            key="audio_uploader",
        )

        if uploaded_file is not None:
            source_type = "audio"

            st.success("Audio uploaded successfully!")

            st.caption(f"{uploaded_file.name}")

    elif source_option == "Web URL":

        source = st.text_input(
            "Enter webpage URL",
            placeholder="https://example.com",
        )

        if source and source.strip():
            source = source.strip()
            source_type = "url"

            st.success("Webpage source selected!")

    elif source_option == "Wikipedia":

        source = st.text_input(
            "Enter Wikipedia topic",
            placeholder="Artificial intelligence",
        )

        if source and source.strip():
            source = source.strip()
            source_type = "wikipedia"

            st.success("Wikipedia topic selected!")


    st.divider()

    max_attempts = st.slider(
        "Maximum Generator Attempts",
        min_value=1,
        max_value=4,
        value=4,
    )

    if st.button(
        "New Conversation",
        use_container_width=True,
    ):
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.rerun()


if source_type in ("url", "wikipedia"):
    source_ready = bool(source)

elif source_type in ("file", "audio"):
    source_ready = uploaded_file is not None

else:
    source_ready = False

st.session_state.source = source
st.session_state.source_type = source_type


if source_ready:

    if uploaded_file is not None:
        source_name = uploaded_file.name
    else:
        source_name = source

    st.sidebar.success("Source is ready.")

    st.sidebar.caption(
        f"Selected source: {source_name}"
    )

else:
    st.sidebar.info(
        "Select or upload a source before asking a question."
    )


for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])



question = st.chat_input(
    "Ask a question about your selected source..."
)


if question:

    if not source_ready:

        st.warning(
            "Please upload a file, audio, or enter a URL/Wikipedia topic first."
        )

    else:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.chat_message("user"):
            st.markdown(question)


        try:

            with st.chat_message("assistant"):

                with st.spinner(
                    "Reading source and generating an answer..."
                ):

                    if source_type in ("file", "audio"):

                        with tempfile.TemporaryDirectory() as temp_dir:

                            file_path = (
                                Path(temp_dir) / uploaded_file.name
                            )

                            file_path.write_bytes(
                                uploaded_file.getvalue()
                            )

                            result = process_source_question(
                                source=str(file_path),
                                source_type=source_type,
                                question=question,
                                conversation_id=st.session_state.conversation_id,
                                max_attempts=max_attempts,
                            )

                    else:

                        result = process_source_question(
                            source=source,
                            source_type=source_type,
                            question=question,
                            conversation_id=st.session_state.conversation_id,
                            max_attempts=max_attempts,
                        )

                st.session_state.conversation_id = result[
                    "conversation_id"
                ]

                answer = (
                    result.get("answer")
                    or "No answer was generated."
                )

                decision = result.get(
                    "decision",
                    "unknown",
                )

                attempts_used = result.get(
                    "attempts_used",
                    0,
                )

                is_cached = result.get(
                    "cached",
                    False,
                )

                st.markdown(answer)


                if is_cached:

                    st.caption(
                        "⚡ Retrieved from semantic cache."
                    )

                else:

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(
                            "Evaluator Decision",
                            decision.upper(),
                        )

                    with col2:
                        st.metric(
                            "Attempts Used",
                            attempts_used,
                        )


                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )


        except ValueError as error:

            st.error(f"Input error: {error}")

        except Exception as error:

            st.error(
                "Something went wrong while processing your question."
            )

            st.exception(error)
