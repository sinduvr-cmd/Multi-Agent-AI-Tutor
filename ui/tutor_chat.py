"""
UI Module: AI Tutor Chat
Conversational tutoring interface grounded strictly in uploaded chapter text.
Cites page references and politely declines out-of-scope inquiries.
"""

import streamlit as st
import database.db as db
from orchestration.tutor_flow import TutorFlow


def render_tutor_chat(flow: TutorFlow):
    st.markdown("""
    <div class="tutor-hero-card">
        <div class="tutor-hero-title">💬 1-on-1 AI Tutor Chat</div>
        <div class="tutor-hero-subtitle">
            Chat with Agent 2 (Expert AI Tutor). Ask questions, request hints, or clarify tricky concepts. 
            All explanations are strictly grounded in your uploaded chapter.
        </div>
    </div>
    """, unsafe_allow_html=True)

    documents = db.list_documents()
    if not documents:
        st.warning("Please upload a textbook chapter first to enable grounded tutoring.")
        return

    doc_options = {d["document_id"]: f"{d['title']} ({d['grade']})" for d in documents}
    selected_doc_id = st.selectbox(
        "Active Chapter Context:",
        options=list(doc_options.keys()),
        format_func=lambda x: doc_options[x],
        index=0 if "selected_document_id" not in st.session_state or st.session_state["selected_document_id"] not in doc_options else list(doc_options.keys()).index(st.session_state["selected_document_id"])
    )

    # Initialize chat history in session state
    chat_key = f"chat_history_{selected_doc_id}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = [
            {"role": "assistant", "content": f"Hello! I am your AI Math Tutor for **{doc_options[selected_doc_id]}**. What concept would you like to explore today?"}
        ]

    # Quick prompt chips
    st.markdown("##### Quick Questions:")
    col_q1, col_q2, col_q3 = st.columns(3)
    quick_query = None
    with col_q1:
        if st.button("📐 Explain Perimeter vs Area", use_container_width=True):
            quick_query = "What is the key difference between perimeter and area?"
    with col_q2:
        if st.button("🔢 How to Add Unlike Fractions", use_container_width=True):
            quick_query = "How do I add two unlike fractions step-by-step?"
    with col_q3:
        if st.button("🏡 Solved Flooring Word Problem", use_container_width=True):
            quick_query = "Can you show me a solved example of a room tiling/flooring problem?"

    # Display chat conversation
    for msg in st.session_state[chat_key]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    user_input = st.chat_input("Ask a question about this chapter...") or quick_query

    if user_input:
        # Display user message
        st.session_state[chat_key].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Retrieve chapter chunks for grounding
        chunks = db.get_document_chunks(selected_doc_id)
        context_text = "\n\n".join([c["content"] for c in chunks[:12]])

        # Generate Tutor response
        with st.chat_message("assistant"):
            with st.spinner("AI Tutor is reviewing textbook context..."):
                response = flow.teaching_agent.chat_response(
                    student_query=user_input,
                    chat_history=st.session_state[chat_key],
                    chapter_context=context_text
                )
                st.markdown(response)
                st.session_state[chat_key].append({"role": "assistant", "content": response})
