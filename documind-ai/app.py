# # app.py

# import os
# import ssl
# import uuid
# import time
# import gc
# import shutil
# import tempfile

# import streamlit as st
# from ingestion.parser import parse_document
# from ingestion.chunker import chunk_document
# from retrieval.vectorstore import store_chunks
# from retrieval.retriever import retrieve_relevant_chunks
# from llm.gemini_client import ask_question

# ssl._create_default_https_context = ssl._create_unverified_context

# # ─────────────────────────────────────────
# # PAGE CONFIG
# # ─────────────────────────────────────────
# st.set_page_config(
#     page_title="DocuMind AI",
#     page_icon="🧠",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # ─────────────────────────────────────────
# # CUSTOM CSS
# # ─────────────────────────────────────────
# st.markdown("""
# <style>
#     .block-container {
#         padding-top: 1rem;
#     }

#     /* User message */
#     .user-row {
#         display: flex;
#         align-items: flex-start;
#         gap: 12px;
#         margin: 16px 0;
#         justify-content: flex-end;
#     }
#     .user-avatar {
#         width: 36px;
#         height: 36px;
#         border-radius: 50%;
#         background: linear-gradient(135deg, #4f6ef7, #7c3aed);
#         display: flex;
#         align-items: center;
#         justify-content: center;
#         font-size: 16px;
#         flex-shrink: 0;
#         color: white;
#         font-weight: bold;
#     }
#     .user-bubble {
#         background-color: #f0f4ff;
#         border: 1px solid #d0d9ff;
#         border-radius: 16px 4px 16px 16px;
#         padding: 12px 16px;
#         max-width: 75%;
#         color: #1a1a1a;
#         font-size: 15px;
#         line-height: 1.5;
#     }
#     .user-name {
#         font-size: 11px;
#         font-weight: 700;
#         color: #4f6ef7;
#         text-align: right;
#         margin-bottom: 4px;
#         margin-right: 48px;
#     }

#     /* Assistant message */
#     .assistant-row {
#         display: flex;
#         align-items: flex-start;
#         gap: 12px;
#         margin: 16px 0;
#         justify-content: flex-start;
#     }
#     .assistant-avatar {
#         width: 36px;
#         height: 36px;
#         border-radius: 50%;
#         background: linear-gradient(135deg, #f97316, #ef4444);
#         display: flex;
#         align-items: center;
#         justify-content: center;
#         font-size: 16px;
#         flex-shrink: 0;
#     }
#     .assistant-bubble {
#         background-color: #fff8f3;
#         border: 1px solid #ffe0c8;
#         border-radius: 4px 16px 16px 16px;
#         padding: 12px 16px;
#         max-width: 75%;
#         color: #1a1a1a;
#         font-size: 15px;
#         line-height: 1.5;
#     }
#     .assistant-name {
#         font-size: 11px;
#         font-weight: 700;
#         color: #f97316;
#         margin-bottom: 4px;
#         margin-left: 48px;
#     }

#     /* App header */
#     .app-header {
#         display: flex;
#         align-items: center;
#         gap: 10px;
#         padding: 8px 0 16px 0;
#         border-bottom: 1px solid #e0e0e0;
#         margin-bottom: 20px;
#     }
#     .app-header h1 {
#         margin: 0;
#         font-size: 26px;
#         font-weight: 700;
#         color: #1a1a1a;
#     }
#     .app-header span {
#         color: #888;
#         font-size: 14px;
#     }

#     [data-testid="stSidebar"] {
#         background-color: #f8f9fb;
#     }
# </style>
# """, unsafe_allow_html=True)

# # ─────────────────────────────────────────
# # SESSION STATE
# # ─────────────────────────────────────────
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []

# if "document_loaded" not in st.session_state:
#     st.session_state.document_loaded = False

# if "full_text" not in st.session_state:
#     st.session_state.full_text = ""

# if "current_file" not in st.session_state:
#     st.session_state.current_file = ""

# if "collection_name" not in st.session_state:
#     st.session_state.collection_name = "documind_collection"

# if "pending_question" not in st.session_state:
#     st.session_state.pending_question = None

# if "total_chunks" not in st.session_state:
#     st.session_state.total_chunks = 0

# # ─────────────────────────────────────────
# # SIDEBAR
# # ─────────────────────────────────────────
# with st.sidebar:
#     st.markdown("""
#         <div style="display:flex; align-items:center; gap:10px;
#                     padding: 8px 0 16px 0;
#                     border-bottom: 1px solid #e0e0e0;
#                     margin-bottom: 16px;">
#             <span style="font-size:28px;">🧠</span>
#             <div>
#                 <div style="font-weight:700; font-size:18px;
#                             color:#1a1a1a;">DocuMind AI</div>
#                 <div style="font-size:11px; color:#888;">
#                     Your documents, your answers.
#                 </div>
#             </div>
#         </div>
#     """, unsafe_allow_html=True)

#     st.subheader("📂 Upload Document")
#     st.caption("Supported: PDF, Word (.docx)")

#     uploaded_file = st.file_uploader(
#         "Choose a file",
#         type=["pdf", "docx"],
#         label_visibility="collapsed"
#     )

#     if uploaded_file:
#         if uploaded_file.name != st.session_state.current_file:
#             with st.spinner("📖 Reading and indexing..."):
#                 try:
#                     suffix = os.path.splitext(uploaded_file.name)[1]
#                     with tempfile.NamedTemporaryFile(
#                         delete=False, suffix=suffix
#                     ) as tmp_file:
#                         tmp_file.write(uploaded_file.read())
#                         tmp_path = tmp_file.name

#                     new_collection = f"documind_{uuid.uuid4().hex[:8]}"

#                     text = parse_document(tmp_path)
#                     chunks = chunk_document(
#                         text, source_name=uploaded_file.name
#                     )
#                     store_chunks(chunks, collection_name=new_collection)

#                     # Save total chunks for dynamic retrieval
#                     st.session_state.total_chunks = len(chunks)

#                     st.session_state.full_text = text
#                     st.session_state.document_loaded = True
#                     st.session_state.current_file = uploaded_file.name
#                     st.session_state.collection_name = new_collection
#                     st.session_state.chat_history = []
#                     st.session_state.pending_question = None

#                     os.unlink(tmp_path)
#                     st.success(f"✅ **{uploaded_file.name}** ready!")

#                 except Exception as e:
#                     st.error(f"❌ Failed to process: {str(e)}")
#         else:
#             st.success(f"✅ **{uploaded_file.name}** loaded!")

#     st.divider()

#     if st.session_state.document_loaded:
#         st.info(f"📄 **Active:** {st.session_state.current_file}")

#     if st.session_state.chat_history:
#         st.divider()
#         if st.button("🗑️ Clear Chat", use_container_width=True):
#             st.session_state.chat_history = []
#             st.session_state.pending_question = None
#             st.rerun()

#     st.markdown("""
#         <div style="position:fixed; bottom:20px; font-size:11px; color:#bbb;">
#             DocuMind AI — Phase 1 Build
#         </div>
#     """, unsafe_allow_html=True)

# # ─────────────────────────────────────────
# # HELPER — Render a single message
# # ─────────────────────────────────────────
# def render_message(role: str, content: str):
#     if role == "user":
#         st.markdown(f'<div class="user-name">You</div>', unsafe_allow_html=True)
#         st.markdown(f"""
#             <div class="user-row">
#                 <div class="user-bubble">{content}</div>
#                 <div class="user-avatar">👤</div>
#             </div>
#         """, unsafe_allow_html=True)
#     else:
#         st.markdown(
#             '<div class="assistant-name">🧠 DocuMind AI</div>',
#             unsafe_allow_html=True
#         )
#         col1, col2 = st.columns([0.04, 0.96])
#         with col1:
#             st.markdown("""
#                 <div class="assistant-avatar">🤖</div>
#             """, unsafe_allow_html=True)
#         with col2:
#             st.markdown(f"""
#                 <div class="assistant-bubble">{content}</div>
#             """, unsafe_allow_html=True)

# # ─────────────────────────────────────────
# # MAIN AREA HEADER
# # ─────────────────────────────────────────
# st.markdown("""
#     <div class="app-header">
#         <span style="font-size:32px;">🧠</span>
#         <div>
#             <h1>DocuMind AI</h1>
#             <span>Upload a document, then ask anything about it.</span>
#         </div>
#     </div>
# """, unsafe_allow_html=True)

# # ─────────────────────────────────────────
# # CHAT HISTORY
# # ─────────────────────────────────────────
# if not st.session_state.chat_history and not st.session_state.pending_question:
#     if st.session_state.document_loaded:
#         st.info("💬 Document loaded! Ask your first question below.")
#     else:
#         st.info("👈 Upload a PDF or Word document from the sidebar to get started.")

# # Render existing chat history
# for message in st.session_state.chat_history:
#     render_message(message["role"], message["content"])

# # ─────────────────────────────────────────
# # HANDLE PENDING QUESTION
# # Shows question immediately, then generates
# # answer — so user always sees their question
# # ─────────────────────────────────────────
# if st.session_state.pending_question:
#     question = st.session_state.pending_question

#     # Show the question immediately
#     render_message("user", question)

#     # Generate answer with spinner
#     with st.spinner("🔍 Searching and generating answer..."):
#         try:
#             # relevant_chunks = retrieve_relevant_chunks(
#             #     question,
#             #     collection_name=st.session_state.collection_name
#             # )
#             relevant_chunks = retrieve_relevant_chunks(
#                 question,
#                 collection_name=st.session_state.collection_name,
#                 total_chunks=st.session_state.total_chunks
#             )
#             answer = ask_question(
#                 question,
#                 relevant_chunks,
#                 full_text=st.session_state.full_text
#             )
#         except Exception as e:
#             error_msg = str(e)
#             if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
#                 answer = "⚠️ Rate limit reached. Please wait a minute and try again."
#             elif "SSL" in error_msg:
#                 answer = "⚠️ Network SSL error. Please check your connection."
#             else:
#                 answer = f"❌ Error: {error_msg}"

#     # Save both to history
#     st.session_state.chat_history.append({
#         "role": "user",
#         "content": question
#     })
#     st.session_state.chat_history.append({
#         "role": "assistant",
#         "content": answer
#     })

#     # Clear pending and rerun to render cleanly
#     st.session_state.pending_question = None
#     st.rerun()

# # ─────────────────────────────────────────
# # CHAT INPUT
# # ─────────────────────────────────────────
# if prompt := st.chat_input(
#     "Ask something about your document...",
#     disabled=not st.session_state.document_loaded
# ):
#     # Store as pending — shows immediately on next render
#     st.session_state.pending_question = prompt
#     st.rerun()


# app.py

import os
import ssl
import re
import time
import tempfile

import streamlit as st
import streamlit.components.v1 as components
from ingestion.parser import parse_document
from ingestion.chunker import chunk_document
from retrieval.vectorstore import (
    store_chunks,
    get_all_sources,
    get_chunk_count_per_source,
    delete_document,
    document_exists,
    get_total_chunks
)
from retrieval.retriever import retrieve_relevant_chunks
from llm.gemini_client import ask_question, detect_greeting
from utils.logger import get_logger

ssl._create_default_https_context = ssl._create_unverified_context
logger = get_logger()

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1rem; }

    /* YOU — right side */
    .user-name {
        font-size: 11px; font-weight: 700;
        color: #4f6ef7; text-align: right;
        margin-bottom: 4px; margin-right: 12px;
    }
    .user-row {
        display: flex; align-items: flex-start;
        gap: 12px; margin: 16px 0; justify-content: flex-end;
    }
    .user-avatar {
        width: 38px; height: 38px; border-radius: 50%;
        background: linear-gradient(135deg, #4f6ef7, #7c3aed);
        display: flex; align-items: center; justify-content: center;
        font-size: 15px; font-weight: 700; flex-shrink: 0;
        color: white; letter-spacing: 0;
    }
    .user-bubble {
        background-color: #f0f4ff; border: 1px solid #d0d9ff;
        border-radius: 16px 4px 16px 16px;
        padding: 12px 16px; max-width: 70%;
        color: #1a1a1a; font-size: 15px; line-height: 1.5;
    }

    /* DOCUMIND AI — left side */
    .assistant-name {
        font-size: 11px; font-weight: 700;
        color: #f97316; margin-bottom: 4px; margin-left: 12px;
    }
    .assistant-row {
        display: flex; align-items: flex-start;
        gap: 12px; margin: 16px 0; justify-content: flex-start;
    }
    .assistant-avatar {
        width: 38px; height: 38px; border-radius: 50%;
        background: linear-gradient(135deg, #f97316, #ef4444);
        display: flex; align-items: center; justify-content: center;
        font-size: 15px; font-weight: 700; flex-shrink: 0;
        color: white;
    }
    .assistant-bubble {
        background-color: #fff8f3; border: 1px solid #ffe0c8;
        border-radius: 4px 16px 16px 16px;
        padding: 12px 16px; max-width: 70%;
        color: #1a1a1a; font-size: 15px; line-height: 1.6;
    }

    /* App header */
    .app-header {
        display: flex; align-items: center; gap: 10px;
        padding: 8px 0 16px 0;
        border-bottom: 1px solid #e0e0e0; margin-bottom: 20px;
    }
    .app-header h1 {
        margin: 0; font-size: 26px;
        font-weight: 700; color: #1a1a1a;
    }
    .app-header span { color: #888; font-size: 14px; }

    [data-testid="stSidebar"] { background-color: #f8f9fb; }

    .processing-banner {
        background: #fff3cd; border: 1px solid #ffc107;
        border-radius: 8px; padding: 10px 14px;
        font-size: 13px; color: #856404;
        margin-bottom: 12px; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# CACHED DB CALLS
# ─────────────────────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def cached_get_all_sources():
    return get_all_sources()

@st.cache_data(ttl=60, show_spinner=False)
def cached_chunk_counts():
    return get_chunk_count_per_source()

@st.cache_data(ttl=60, show_spinner=False)
def cached_total_chunks():
    return get_total_chunks()

# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "full_texts" not in st.session_state:
    st.session_state.full_texts = {}

if "docs_loaded" not in st.session_state:
    st.session_state.docs_loaded = cached_get_all_sources()

if "processing" not in st.session_state:
    st.session_state.processing = None

if "show_uploader" not in st.session_state:
    st.session_state.show_uploader = True

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def format_response(content: str) -> str:
    """Convert markdown to HTML for assistant bubble."""
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    lines = content.split('\n')
    html_lines = []
    in_ul = False
    in_ol = False
    in_table = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith('* ') or stripped.startswith('- '):
            if in_ol: html_lines.append('</ol>'); in_ol = False
            if in_table: html_lines.append('</table>'); in_table = False
            if not in_ul:
                html_lines.append('<ul style="margin:8px 0;padding-left:20px;">')
                in_ul = True
            item = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', stripped[2:])
            html_lines.append(f'<li style="margin:4px 0;">{item}</li>')

        elif re.match(r'^\d+\.\s', stripped):
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if in_table: html_lines.append('</table>'); in_table = False
            if not in_ol:
                html_lines.append('<ol style="margin:8px 0;padding-left:20px;">')
                in_ol = True
            item_text = re.sub(r'^\d+\.\s', '', stripped)
            item_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', item_text)
            html_lines.append(f'<li style="margin:4px 0;">{item_text}</li>')

        elif '|' in stripped and stripped.startswith('|'):
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            cells = [c.strip() for c in stripped.split('|') if c.strip()]
            if all(set(c) <= set('-+: ') for c in cells):
                continue
            if not in_table:
                html_lines.append(
                    '<table style="border-collapse:collapse;width:100%;margin:8px 0;">'
                )
                in_table = True
                tag = 'th'
            else:
                tag = 'td'
            row_html = '<tr>'
            for cell in cells:
                row_html += (
                    f'<{tag} style="border:1px solid #ddd;'
                    f'padding:6px 10px;text-align:left;">{cell}</{tag}>'
                )
            row_html += '</tr>'
            html_lines.append(row_html)

        elif stripped.startswith('### '):
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            if in_table: html_lines.append('</table>'); in_table = False
            html_lines.append(f'<h4 style="margin:12px 0 4px 0;">{stripped[4:]}</h4>')
        elif stripped.startswith('## '):
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            if in_table: html_lines.append('</table>'); in_table = False
            html_lines.append(f'<h3 style="margin:12px 0 4px 0;">{stripped[3:]}</h3>')
        elif stripped.startswith('# '):
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            if in_table: html_lines.append('</table>'); in_table = False
            html_lines.append(f'<h2 style="margin:12px 0 4px 0;">{stripped[2:]}</h2>')
        else:
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            if in_table: html_lines.append('</table>'); in_table = False
            if stripped:
                html_lines.append(f'<p style="margin:6px 0;">{stripped}</p>')

    if in_ul: html_lines.append('</ul>')
    if in_ol: html_lines.append('</ol>')
    if in_table: html_lines.append('</table>')
    return '\n'.join(html_lines)


def render_copy_button(content: str, key: str):
    """
    Renders a working copy button using st.components.v1.html
    This is the only way to run JavaScript in Streamlit properly.
    The button copies plain text content to clipboard.
    """
    # Escape content for safe JS string
    safe_content = content.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')

    copy_html = f"""
    <div style="margin: -4px 0 8px 0;">
        <button id="copybtn_{key}"
            onclick="
                navigator.clipboard.writeText(`{safe_content}`)
                .then(() => {{
                    document.getElementById('copybtn_{key}').innerHTML = '✅ Copied!';
                    document.getElementById('copybtn_{key}').style.color = '#16a34a';
                    document.getElementById('copybtn_{key}').style.borderColor = '#16a34a';
                    setTimeout(() => {{
                        document.getElementById('copybtn_{key}').innerHTML = '&#128203; Copy';
                        document.getElementById('copybtn_{key}').style.color = '#888';
                        document.getElementById('copybtn_{key}').style.borderColor = '#e0e0e0';
                    }}, 2000);
                }})
                .catch(() => {{
                    document.getElementById('copybtn_{key}').innerHTML = '❌ Failed';
                }});"
            style="
                background: none;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 12px;
                color: #888;
                cursor: pointer;
                font-family: sans-serif;
                display: inline-flex;
                align-items: center;
                gap: 4px;
                transition: all 0.2s;">
            &#128203; Copy
        </button>
    </div>
    """
    components.html(copy_html, height=45)


def render_message(role: str, content: str, msg_index: int = 0):
    """
    Render chat message.
    User — right side, purple avatar with 'Y' initial
    DocuMind — left side, orange avatar with 'D' initial + copy button
    """
    if role == "user":
        st.markdown('<div class="user-name">You</div>', unsafe_allow_html=True)
        st.markdown(f"""
            <div class="user-row">
                <div class="user-bubble">{content}</div>
                <div class="user-avatar">Y</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        formatted = format_response(content)
        st.markdown(
            '<div class="assistant-name">DocuMind AI</div>',
            unsafe_allow_html=True
        )
        st.markdown(f"""
            <div class="assistant-row">
                <div class="assistant-avatar">D</div>
                <div class="assistant-bubble">{formatted}</div>
            </div>
        """, unsafe_allow_html=True)

        # Render working copy button via components.html
        render_copy_button(content, key=f"msg_{msg_index}")


def process_file(uploaded_file) -> bool:
    """Parse, chunk and index a single uploaded file."""
    source_name = uploaded_file.name
    if source_name in st.session_state.docs_loaded:
        return False
    try:
        suffix = os.path.splitext(source_name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        text = parse_document(tmp_path)
        chunks = chunk_document(text, source_name=source_name)
        store_chunks(chunks)

        st.session_state.full_texts[source_name] = text
        if source_name not in st.session_state.docs_loaded:
            st.session_state.docs_loaded.append(source_name)

        os.unlink(tmp_path)
        logger.info(f"✅ Indexed: {source_name}")
        return True

    except Exception as e:
        logger.error(f"Failed: {source_name} — {e}")
        st.sidebar.error(f"❌ Failed: {source_name} — {str(e)}")
        return False


# ─────────────────────────────────────────
# PROCESSING STATE
# ─────────────────────────────────────────
is_processing = st.session_state.processing is not None

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:

    st.markdown("""
        <div style="display:flex; align-items:center; gap:10px;
                    padding:8px 0 16px 0;
                    border-bottom:1px solid #e0e0e0; margin-bottom:16px;">
            <div style="width:36px; height:36px; border-radius:50%;
                        background:linear-gradient(135deg,#f97316,#ef4444);
                        display:flex; align-items:center; justify-content:center;
                        font-size:16px; font-weight:700; color:white;">D</div>
            <div>
                <div style="font-weight:700; font-size:18px; color:#1a1a1a;">
                    DocuMind AI
                </div>
                <div style="font-size:11px; color:#888;">
                    Your documents, your answers.
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if is_processing:
        messages = {
            "indexing": "📖 Indexing document... please wait.",
            "deleting": "🗑️ Removing document... please wait.",
        }
        st.markdown(
            f'<div class="processing-banner">'
            f'{messages.get(st.session_state.processing, "⏳ Processing...")}'
            f'</div>',
            unsafe_allow_html=True
        )

    st.subheader("📂 Upload Documents")
    st.caption("Supported: PDF, Word (.docx) — upload one or many")

    if st.session_state.show_uploader:
        uploaded_files = st.file_uploader(
            "Choose files",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            disabled=is_processing,
            key=f"uploader_{st.session_state.uploader_key}"
        )

        if uploaded_files and not is_processing:
            new_files = [
                f for f in uploaded_files
                if f.name not in st.session_state.docs_loaded
            ]
            if new_files:
                st.session_state.processing = "indexing"
                st.rerun()

        if st.session_state.processing == "indexing" and uploaded_files:
            new_files = [
                f for f in uploaded_files
                if f.name not in st.session_state.docs_loaded
            ]
            if new_files:
                progress = st.progress(0)
                status = st.empty()
                indexed_count = 0
                for idx, file in enumerate(new_files):
                    status.info(f"📖 Indexing **{file.name}**...")
                    success = process_file(file)
                    if success:
                        indexed_count += 1
                    progress.progress((idx + 1) / len(new_files))
                progress.empty()
                status.empty()
                st.session_state.processing = None
                if indexed_count > 0:
                    st.session_state.show_uploader = False
                    st.cache_data.clear()
                    st.rerun()
            else:
                st.session_state.processing = None
    else:
        st.info("✅ Documents indexed successfully!")
        if st.button(
            "➕ Add More Documents",
            use_container_width=True,
            disabled=is_processing
        ):
            st.session_state.show_uploader = True
            st.session_state.uploader_key += 1
            st.rerun()

    st.divider()

    if st.session_state.docs_loaded:
        st.subheader("📚 Loaded Documents")
        chunk_counts = cached_chunk_counts()

        for doc_name in list(st.session_state.docs_loaded):
            col1, col2 = st.columns([0.78, 0.22])
            with col1:
                count = chunk_counts.get(doc_name, 0)
                st.markdown(f"""
                    <div style="font-size:13px; font-weight:500;
                                color:#1a1a1a; padding:6px 0;
                                overflow:hidden; text-overflow:ellipsis;
                                white-space:nowrap;" title="{doc_name}">
                        📄 {doc_name}
                    </div>
                    <div style="font-size:10px; color:#888; margin-bottom:6px;">
                        {count} chunks
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button(
                    "🗑️",
                    key=f"del_{doc_name}",
                    help=f"Remove {doc_name}",
                    disabled=is_processing
                ):
                    st.session_state.processing = "deleting"
                    st.session_state._doc_to_delete = doc_name
                    st.rerun()

        if st.session_state.processing == "deleting":
            doc_to_delete = st.session_state.get("_doc_to_delete")
            if doc_to_delete:
                delete_document(doc_to_delete)
                if doc_to_delete in st.session_state.docs_loaded:
                    st.session_state.docs_loaded.remove(doc_to_delete)
                if doc_to_delete in st.session_state.full_texts:
                    del st.session_state.full_texts[doc_to_delete]
                st.session_state._doc_to_delete = None
                st.session_state.processing = None
                st.session_state.show_uploader = False
                st.session_state.uploader_key += 1
                st.cache_data.clear()
                st.rerun()

        st.divider()

    if st.session_state.chat_history:
        if st.button(
            "🗑️ Clear Chat",
            use_container_width=True,
            type="secondary",
            disabled=is_processing
        ):
            st.session_state.chat_history = []
            st.rerun()

    st.markdown("""
        <div style="font-size:11px; color:#bbb;
                    margin-top:24px; padding-top:8px;
                    border-top:1px solid #eee;">
            DocuMind AI — Phase 2 Build
        </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# MAIN AREA HEADER
# ─────────────────────────────────────────
st.markdown("""
    <div class="app-header">
        <div style="width:42px; height:42px; border-radius:50%;
                    background:linear-gradient(135deg,#f97316,#ef4444);
                    display:flex; align-items:center; justify-content:center;
                    font-size:20px; font-weight:700; color:white; flex-shrink:0;">
            D
        </div>
        <div>
            <h1>DocuMind AI</h1>
            <span>Upload documents, then ask anything about them.</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# CHAT HISTORY
# ─────────────────────────────────────────
has_docs = len(st.session_state.docs_loaded) > 0

if not st.session_state.chat_history:
    if has_docs:
        doc_list = ", ".join(st.session_state.docs_loaded)
        st.info(
            f"💬 **{len(st.session_state.docs_loaded)} document(s) loaded:** "
            f"{doc_list}. Ask anything!"
        )
    else:
        st.info(
            "👈 Upload PDF or Word documents from the sidebar to get started."
        )

for idx, message in enumerate(st.session_state.chat_history):
    render_message(message["role"], message["content"], msg_index=idx)

# ─────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────
chat_disabled = not has_docs or is_processing

if prompt := st.chat_input(
    "Ask something about your documents..." if not is_processing else "Please wait...",
    disabled=chat_disabled
):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    render_message("user", prompt, msg_index=len(st.session_state.chat_history))

    with st.spinner("🔍 Thinking..."):
        try:
            greeting = detect_greeting(prompt)
            if greeting:
                answer = greeting
            else:
                total = cached_total_chunks()
                chunks = retrieve_relevant_chunks(prompt, total_chunks=total)
                answer = ask_question(
                    prompt,
                    chunks,
                    full_texts=st.session_state.full_texts
                )
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                answer = "⚠️ Rate limit reached. Please wait a minute and try again."
            elif "503" in err or "UNAVAILABLE" in err:
                answer = "⚠️ Model overloaded. Please wait 30 seconds and try again."
            elif "SSL" in err:
                answer = "⚠️ Network SSL error. Please check your connection."
            else:
                answer = f"❌ Error: {err}"

    render_message(
        "assistant", answer,
        msg_index=len(st.session_state.chat_history) + 1
    )
    st.session_state.chat_history.append({"role": "assistant", "content": answer})