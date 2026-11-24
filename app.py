import os

import requests
import streamlit as st

from core.i18n import LANGUAGE_LABELS, translate


st.set_page_config(
    page_title="Ders Ofisi",
    page_icon="D",
    layout="wide",
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def t(key, **values):
    return translate(st.session_state.get("language", "ar"), key, **values)


def sync_language(widget_key):
    st.session_state["language"] = st.session_state.get(widget_key, "ar")


def choose_language(widget_key):
    current = st.session_state.get("language", "ar")
    selected = st.selectbox(
        t("language"),
        options=list(LANGUAGE_LABELS),
        index=list(LANGUAGE_LABELS).index(current),
        format_func=lambda code: LANGUAGE_LABELS[code],
        key=widget_key,
        on_change=sync_language,
        args=(widget_key,),
    )
    st.session_state["language"] = selected
    apply_language_direction(selected)
    return selected


def apply_language_direction(language):
    if language == "ar":
        st.markdown(
            """
            <style>
            [data-testid="stMain"], [data-testid="stSidebar"] {
                direction: rtl;
                text-align: right;
            }
            [data-testid="stSidebar"] [role="radiogroup"] label {
                flex-direction: row-reverse;
                text-align: right;
            }
            [data-testid="stTextInput"] input,
            [data-testid="stTextArea"] textarea,
            [data-testid="stSelectbox"] [data-baseweb="select"] {
                direction: rtl;
                text-align: right;
            }
            [data-testid="stFileUploader"], [data-testid="stMetric"],
            [data-testid="stDataFrame"] {
                direction: rtl;
                text-align: right;
            }
            [data-testid="stMain"] [data-testid="stHorizontalBlock"] {
                direction: rtl;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    """
    <style>
    :root {
        --ink: #1d2b3a;
        --muted: #687787;
        --paper: #f4f6f8;
        --line: #e1e6eb;
        --navy: #172b40;
        --navy-light: #243d56;
        --teal: #247a73;
        --teal-dark: #1a625c;
        --gold: #c8a76a;
    }

    html, body, [class*="css"] {
        font-family: "Inter", "Segoe UI", sans-serif;
        color: var(--ink);
    }

    [data-testid="stAppViewContainer"] {
        background: var(--paper);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    .stAppDeployButton {
        display: none !important;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1120px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    [data-testid="stSidebar"] {
        background: var(--navy);
        border-right: 1px solid rgba(255, 255, 255, .08);
    }

    [data-testid="stSidebar"] > div:first-child {
        background: var(--navy);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #d9e1e9;
    }

    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #d9e1e9 !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] {
        gap: .35rem;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label {
        border-radius: 9px;
        padding: .6rem .65rem;
        transition: background .15s ease;
    }

    [data-testid="stSidebar"] input[type="radio"] {
        accent-color: var(--gold) !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(255, 255, 255, .07);
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background: var(--navy-light);
    }

    [data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"] > div > div:first-child {
        border-color: var(--gold) !important;
        background: var(--gold) !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"] > div > div:first-child > div {
        background: var(--gold) !important;
    }

    .side-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 1.3rem .2rem 1.6rem;
        border-bottom: 1px solid rgba(255, 255, 255, .12);
        margin-bottom: 1.6rem;
    }

    .side-brand-mark {
        display: grid;
        place-items: center;
        width: 38px;
        height: 38px;
        border: 1px solid rgba(200, 167, 106, .75);
        border-radius: 10px;
        color: #e5cc9d;
        font-family: Georgia, serif;
        font-size: 20px;
        font-weight: 600;
    }

    .side-brand-name {
        color: #f5f7f9;
        font-size: 15px;
        font-weight: 650;
        letter-spacing: .01em;
    }

    .side-brand-subtitle {
        margin-top: 3px;
        color: #9eafbf;
        font-size: 9px;
        font-weight: 650;
        letter-spacing: .14em;
    }

    .side-section-label {
        color: #93a5b6;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: .14em;
        text-transform: uppercase;
        margin: 0 0 .35rem .65rem;
    }

    .side-note {
        margin-top: 2rem;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, .12);
        border-radius: 10px;
        background: rgba(255, 255, 255, .035);
    }

    .side-note-kicker {
        color: #d8c18f;
        font-size: 9px;
        font-weight: 700;
        letter-spacing: .13em;
    }

    .side-note-copy {
        margin-top: 8px;
        color: #c5d0da;
        font-size: 12px;
        line-height: 1.55;
    }

    .login-shell {
        padding: 3.8rem 0 2rem;
    }

    .login-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 3.1rem;
    }

    .login-brand-mark {
        display: grid;
        place-items: center;
        width: 43px;
        height: 43px;
        border: 1px solid #c8a76a;
        border-radius: 11px;
        color: #9b7b43;
        font-family: Georgia, serif;
        font-size: 22px;
        font-weight: 600;
    }

    .login-brand-name {
        color: var(--ink);
        font-size: 16px;
        font-weight: 700;
    }

    .login-brand-subtitle {
        margin-top: 3px;
        color: var(--muted);
        font-size: 9px;
        font-weight: 700;
        letter-spacing: .14em;
    }

    .login-copy {
        max-width: 510px;
        padding: 1.5rem 1rem 1.5rem 0;
    }

    .login-copy h1 {
        margin: .8rem 0 1rem;
        color: var(--ink);
        font-family: Georgia, "Times New Roman", serif;
        font-size: clamp(36px, 4vw, 52px);
        font-weight: 500;
        letter-spacing: -.04em;
        line-height: 1.08;
    }

    .login-copy p {
        max-width: 470px;
        color: var(--muted);
        font-size: 15px;
        line-height: 1.75;
    }

    .login-assurance {
        display: flex;
        align-items: flex-start;
        gap: 13px;
        margin-top: 2.1rem;
        padding-top: 1.35rem;
        border-top: 1px solid var(--line);
        color: #52616f;
        font-size: 12px;
        line-height: 1.6;
    }

    .login-assurance-mark {
        display: grid;
        place-items: center;
        flex: 0 0 28px;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: #e6f0ed;
        color: var(--teal-dark);
        font-size: 13px;
        font-weight: 700;
    }

    .login-card {
        margin-top: 1.4rem;
        padding: 2rem 2rem 1.7rem;
        border: 1px solid var(--line);
        border-radius: 14px;
        background: #fff;
        box-shadow: 0 18px 55px rgba(26, 43, 59, .07);
    }

    .login-card h2 {
        margin: 0 0 .45rem;
        color: var(--ink);
        font-family: Georgia, "Times New Roman", serif;
        font-size: 27px;
        font-weight: 500;
    }

    .login-card-copy {
        margin-bottom: 1.7rem;
        color: var(--muted);
        font-size: 13px;
        line-height: 1.6;
    }

    .login-footnote {
        margin-top: 1rem;
        color: #81909c;
        font-size: 11px;
        line-height: 1.55;
        text-align: center;
    }

    .masthead {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 2rem;
        padding: .25rem 0 1.55rem;
        border-bottom: 1px solid var(--line);
        margin-bottom: 2.4rem;
    }

    .masthead-kicker, .page-kicker {
        color: var(--teal);
        font-size: 10px;
        font-weight: 750;
        letter-spacing: .15em;
        text-transform: uppercase;
    }

    .masthead h1 {
        margin: .45rem 0 .4rem;
        color: var(--ink);
        font-family: Georgia, "Times New Roman", serif;
        font-size: clamp(29px, 3vw, 38px);
        font-weight: 500;
        letter-spacing: -.035em;
        line-height: 1.12;
    }

    .masthead-copy {
        max-width: 690px;
        color: var(--muted);
        font-size: 14px;
        line-height: 1.6;
    }

    .workspace-badge {
        display: inline-flex;
        align-items: center;
        gap: 9px;
        margin-top: .3rem;
        padding: 9px 13px;
        border: 1px solid #dce5e4;
        border-radius: 99px;
        background: #fbfcfc;
        color: #526b69;
        font-size: 11px;
        font-weight: 650;
        white-space: nowrap;
    }

    .workspace-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--teal);
    }

    .page-heading {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 1.5rem;
        margin-bottom: 1.35rem;
    }

    .page-heading h2 {
        margin: .45rem 0 .35rem;
        color: var(--ink);
        font-family: Georgia, "Times New Roman", serif;
        font-size: 29px;
        font-weight: 500;
        letter-spacing: -.025em;
        line-height: 1.2;
    }

    .page-heading p {
        max-width: 720px;
        margin: 0;
        color: var(--muted);
        font-size: 14px;
        line-height: 1.6;
    }

    .page-tag {
        flex: 0 0 auto;
        margin-top: .2rem;
        padding: 7px 10px;
        border: 1px solid var(--line);
        border-radius: 6px;
        background: #fff;
        color: #687787;
        font-size: 9px;
        font-weight: 700;
        letter-spacing: .1em;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--line) !important;
        border-radius: 12px !important;
        background: #fff;
        box-shadow: 0 8px 24px rgba(28, 45, 63, .035);
    }

    [data-testid="stForm"] {
        border: 0 !important;
        padding: 0 !important;
    }

    [data-testid="stMain"] h3 {
        margin-bottom: .45rem;
        color: var(--ink);
        font-family: Georgia, "Times New Roman", serif;
        font-size: 27px;
        font-weight: 500;
    }

    [data-testid="stFormSubmitButton"] button {
        min-height: 42px;
        border: 1px solid var(--teal) !important;
        border-radius: 8px !important;
        background: var(--teal) !important;
        color: #fff !important;
        font-weight: 650;
        box-shadow: none !important;
    }

    [data-testid="stFormSubmitButton"] button:hover {
        border-color: var(--teal-dark) !important;
        background: var(--teal-dark) !important;
    }

    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        border-color: #d9e0e6;
        border-radius: 8px;
        background: #fff;
    }

    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--teal);
        box-shadow: 0 0 0 1px var(--teal);
    }

    [data-testid="stFileUploader"] section {
        border: 1px dashed #c6d0d8;
        border-radius: 9px;
        background: #fafbfc;
    }

    .stButton > button[kind="primary"],
    .stDownloadButton > button {
        min-height: 42px;
        border: 1px solid var(--teal) !important;
        border-radius: 8px !important;
        background: var(--teal) !important;
        color: #fff !important;
        font-weight: 650;
        box-shadow: none !important;
        transition: background .15s ease, border-color .15s ease;
    }

    .stButton > button[kind="primary"]:hover,
    .stDownloadButton > button:hover {
        border-color: var(--teal-dark) !important;
        background: var(--teal-dark) !important;
    }

    .stButton > button[kind="secondary"] {
        min-height: 40px;
        border-color: #cfd8df !important;
        border-radius: 8px !important;
        color: #34485b !important;
    }

    [data-testid="stAlert"] {
        border-radius: 9px;
    }

    @media (max-width: 760px) {
        [data-testid="stMainBlockContainer"] {
            padding: 1.3rem 1rem 3rem;
        }
        .masthead {
            display: block;
            margin-bottom: 1.8rem;
        }
        .workspace-badge {
            margin-top: 1rem;
        }
        .page-heading {
            display: block;
        }
        .page-tag {
            display: inline-block;
            margin-top: .9rem;
        }
        .login-shell {
            padding-top: 1.2rem;
        }
        .login-brand {
            margin-bottom: 1.4rem;
        }
        .login-copy {
            padding: .5rem 0;
        }
        .login-card {
            margin-top: 1rem;
            padding: 1.4rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def show_api_error(res):
    try:
        detail = res.json().get("detail", res.text)
    except Exception:
        detail = res.text
    if res.status_code == 401:
        st.error(t("session_expired"))
    elif res.status_code == 503:
        st.error(t("service_not_ready"))
    elif res.status_code == 400:
        st.error(t("request_rejected"))
    elif res.status_code >= 500:
        st.error(t("operation_failed"))
    else:
        st.error(t("api_error", status=res.status_code))
    if detail and res.status_code not in (400, 401, 503) and res.status_code < 500:
        st.caption(str(detail))


def auth_headers():
    token = st.session_state.get("access_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def fetch_courses():
    try:
        res = requests.get(
            f"{API_BASE_URL}/courses", headers=auth_headers(), timeout=10
        )
        if res.status_code == 200:
            return res.json().get("courses", [])
    except Exception:
        pass
    return []


def localize_audit_logs(logs):
    columns = {
        "id": t("column_id"),
        "timestamp": t("column_timestamp"),
        "event_type": t("column_event"),
        "course_name": t("column_course"),
        "subject": t("column_subject"),
        "status": t("column_status"),
        "details": t("column_details"),
    }
    events = {
        "PDF_UPLOAD": t("event_pdf_upload"),
        "CONTENT_GEN": t("event_content_gen"),
        "SECURITY_ALERT": t("event_security_alert"),
    }
    statuses = {
        "SUCCESS": t("status_success"),
        "BLOCKED": t("status_blocked"),
        "FAILED": t("status_failed"),
    }
    localized = []
    for log in logs:
        row = dict(log)
        row["event_type"] = events.get(row.get("event_type"), row.get("event_type"))
        row["status"] = statuses.get(row.get("status"), row.get("status"))
        localized.append({columns[key]: row.get(key) for key in columns})
    return localized


def page_heading(kicker, title, description, tag):
    st.markdown(
        f"""
        <div class="page-heading">
            <div>
                <div class="page-kicker">{kicker}</div>
                <h2>{title}</h2>
                <p>{description}</p>
            </div>
            <div class="page-tag">{tag}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_login():
    lang_col, _ = st.columns([.35, .65])
    with lang_col:
        choose_language("language_before_login")

    st.markdown(
        f"""
        <div class="login-brand">
            <div class="login-brand-mark">D</div>
            <div>
                <div class="login-brand-name">{t('product')}</div>
                <div class="login-brand-subtitle">{t('product_subtitle')}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.08, .92], gap="large", vertical_alignment="center")
    with left:
        st.markdown(
            f"""
            <div class="login-copy">
                <div class="masthead-kicker">{t('admin_workspace')}</div>
                <h1>{t('login_headline')}</h1>
                <p>{t('login_description')}</p>
                <div class="login-assurance">
                    <div class="login-assurance-mark">✓</div>
                    <div><strong>{t('access_heading')}</strong><br>{t('access_description')}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        with st.container(border=True):
            st.markdown(f"### {t('login_title')}")
            st.markdown(
                f'<div class="login-card-copy">{t("login_card_description")}</div>',
                unsafe_allow_html=True,
            )
            with st.form("admin_login_form", clear_on_submit=True, border=False):
                username = st.text_input(
                    t("username"), autocomplete="username", max_chars=128, key="login_username"
                )
                password = st.text_input(
                    t("password"), type="password", autocomplete="current-password",
                    max_chars=1024, key="login_password",
                )
                submitted = st.form_submit_button(
                    t("login_button"), type="primary", use_container_width=True,
                    key="login_submit",
                )

            if submitted:
                if not username or not password:
                    st.warning(t("login_missing"))
                else:
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/auth/login",
                            json={"username": username, "password": password},
                            timeout=12,
                        )
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state["access_token"] = result["access_token"]
                            st.session_state["admin_user"] = result["user"]["username"]
                            st.session_state.pop("expired_session", None)
                            st.rerun()
                        elif response.status_code == 503:
                            st.error(t("login_setup_missing"))
                        elif response.status_code == 401:
                            st.error(t("invalid_login"))
                        else:
                            show_api_error(response)
                    except requests.RequestException:
                        st.error(t("login_unavailable"))

            if st.session_state.pop("expired_session", False):
                st.info(t("session_expired"))
            st.markdown(
                f'<div class="login-footnote">{t("access_heading")} · {t("session_duration")}</div>',
                unsafe_allow_html=True,
            )


def require_ui_session():
    token = st.session_state.get("access_token")
    if not token:
        return False
    try:
        response = requests.get(
            f"{API_BASE_URL}/auth/me", headers=auth_headers(), timeout=8
        )
    except requests.RequestException:
        st.error(t("session_check_unavailable"))
        st.stop()

    if response.status_code == 200:
        st.session_state["admin_user"] = response.json().get("user", {}).get("username", "")
        return True
    if response.status_code == 401:
        st.session_state.pop("access_token", None)
        st.session_state.pop("admin_user", None)
        st.session_state["expired_session"] = True
        return False
    show_api_error(response)
    st.stop()


st.session_state.setdefault("language", "ar")

if not require_ui_session():
    render_login()
    st.stop()

choose_language("language_after_login")

st.sidebar.markdown(
    f"""
    <div class="side-brand">
        <div class="side-brand-mark">D</div>
        <div>
            <div class="side-brand-name">{t('product')}</div>
            <div class="side-brand-subtitle">{t('product_subtitle')}</div>
        </div>
    </div>
    <div class="side-section-label">{t('workspace')}</div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.caption(t("admin_session", username=st.session_state.get("admin_user", "admin")))
if st.sidebar.button(t("logout"), use_container_width=True, key="logout_button"):
    for key in ("access_token", "admin_user", "gen_result", "audit_logs"):
        st.session_state.pop(key, None)
    st.rerun()

menu_labels = {
    "material": "menu_material",
    "content": "menu_content",
    "audit": "menu_audit",
}
menu = st.sidebar.radio(
    t("workspace"),
    list(menu_labels),
    format_func=lambda value: t(menu_labels[value]),
    label_visibility="collapsed",
    key="workspace_menu",
)

st.sidebar.markdown(
    f"""
    <div class="side-note">
        <div class="side-note-kicker">{t('workflow_title')}</div>
        <div class="side-note-copy">{t('workflow_description')}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="masthead">
        <div>
            <div class="masthead-kicker">{t('masthead_kicker')}</div>
            <h1>{t('app_title')}</h1>
            <div class="masthead-copy">{t('app_description')}</div>
        </div>
        <div class="workspace-badge"><span class="workspace-dot"></span>{t('secure_workspace')}</div>
    </div>
    """,
    unsafe_allow_html=True,
)


if menu == "material":
    page_heading(
        t("material_section"),
        t("material_title"),
        t("material_description"),
        t("pdf_only_tag"),
    )

    with st.container(border=True):
        st.markdown(f"**{t('new_source')}**")
        st.caption(t("source_caption"))
        course_name = st.text_input(
            t("course_name"), placeholder=t("course_placeholder"), key="upload_course_name"
        )
        uploaded_file = st.file_uploader(
            t("pdf_label"),
            type=["pdf"],
            help=t("pdf_help"),
            key="course_pdf_upload",
        )

        if st.button(
            t("upload_button"), type="primary", use_container_width=True,
            key="upload_material_button",
        ):
            if not course_name or not uploaded_file:
                st.warning(t("upload_required"))
            else:
                with st.spinner(t("processing_pdf")):
                    files = {
                        "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
                    }
                    data = {"course_name": course_name}

                    try:
                        res = requests.post(
                            f"{API_BASE_URL}/upload-course-pdf",
                            data=data,
                            files=files,
                            headers=auth_headers(),
                            timeout=180,
                        )
                        if res.status_code == 200:
                            result = res.json()
                            st.success(t("upload_success"))
                            col1, col2, col3 = st.columns(3)
                            col1.metric(t("total_pages"), result.get("total_pages"))
                            col2.metric(t("processed_chunks"), result.get("stored_chunks"))
                            col3.metric(
                                t("masked_data_types"), len(result.get("masked_pii_types", []))
                            )
                            if result.get("masked_pii_types"):
                                st.info(
                                    t("masked_types_prefix")
                                    + ", ".join(result.get("masked_pii_types", []))
                                )
                        else:
                            show_api_error(res)
                    except requests.RequestException:
                        st.error(t("upload_connection_error"))

elif menu == "content":
    page_heading(
        t("content_section"),
        t("content_title"),
        t("content_description"),
        t("source_informed_tag"),
    )

    courses = fetch_courses()
    if courses:
        st.caption(t("courses_caption", courses=", ".join(courses)))

    with st.container(border=True):
        st.markdown(f"**{t('content_brief')}**")
        st.caption(t("content_brief_caption"))
        col1, col2 = st.columns([1.15, 0.85])
        with col1:
            course_name = st.text_input(
                t("course_name"), placeholder=t("course_placeholder"), key="generation_course_name"
            )
            topic = st.text_input(
                t("topic"), placeholder=t("topic_placeholder"), key="generation_topic"
            )
        with col2:
            content_type = st.selectbox(
                t("content_format"),
                ["QUIZ", "LECTURE_NOTE", "SLIDE_OUTLINE"],
                format_func=lambda value: {
                    "QUIZ": t("format_quiz"),
                    "LECTURE_NOTE": t("format_notes"),
                    "SLIDE_OUTLINE": t("format_slides"),
                }[value],
                key="content_type",
            )
        current_language = st.session_state.get("language", "ar")
        previous_default_language = st.session_state.get(
            "_content_instructions_default_language"
        )
        instructions_key = "content_instructions"
        if instructions_key not in st.session_state:
            st.session_state[instructions_key] = t("default_instructions")
        elif previous_default_language and previous_default_language != current_language:
            previous_default = translate(previous_default_language, "default_instructions")
            if st.session_state[instructions_key] == previous_default:
                st.session_state[instructions_key] = t("default_instructions")
        st.session_state["_content_instructions_default_language"] = current_language

        raw_instructions = st.text_area(
            t("instructions"),
            max_chars=1500,
            height=130,
            key=instructions_key,
        )

        if st.button(
            t("generate_button"), type="primary", use_container_width=True,
            key="generate_content_button",
        ):
            if not course_name or not topic:
                st.warning(t("content_required"))
            else:
                with st.spinner(t("checking_request")):
                    payload = {
                        "course_name": course_name,
                        "topic": topic,
                        "content_type": content_type,
                        "raw_instructions": raw_instructions,
                        "language": st.session_state.get("language", "ar"),
                    }
                    try:
                        res = requests.post(
                            f"{API_BASE_URL}/generate-content-with-rag",
                            json=payload,
                            headers=auth_headers(),
                            timeout=120,
                        )
                        if res.status_code == 200:
                            st.session_state["gen_result"] = {
                                "data": res.json(),
                                "topic": topic,
                                "language": current_language,
                            }
                        else:
                            st.session_state.pop("gen_result", None)
                            show_api_error(res)
                    except requests.RequestException:
                        st.error(t("generation_connection_error"))

    result = st.session_state.get("gen_result")
    if result:
        data = result["data"]
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(f"**{t('prepared_content')}**")
            sec = data.get("security_checks", {})
            pii = sec.get("masked_pii_types") or []
            source_status = t("source_used") if data.get("rag_context_used") else t("curriculum_used")
            output_language = LANGUAGE_LABELS.get(result.get("language", "tr"), "Türkçe")
            st.caption(
                t("security_checks_complete")
                + " · " + source_status
                + " · " + t("masked_result", types=", ".join(pii) if pii else t("none"))
                + " · " + t("output_language", language=output_language)
            )
            st.markdown(data.get("generated_content", ""))
            st.download_button(
                t("download_markdown"),
                data=data.get("generated_content", ""),
                file_name="icerik.md" if st.session_state["language"] == "tr" else "course_content.md",
                mime="text/markdown",
                key="download_content_button",
            )

elif menu == "audit":
    page_heading(
        t("audit_section"),
        t("audit_title"),
        t("audit_description"),
        t("admin_access_tag"),
    )

    with st.container(border=True):
        st.markdown(f"**{t('audit_card_title')}**")
        st.caption(t("admin_access_active"))

        if st.button(
            t("fetch_logs"), type="primary", use_container_width=True, key="fetch_audit_logs"
        ):
            try:
                res = requests.get(
                    f"{API_BASE_URL}/security-audit-logs",
                    headers=auth_headers(),
                    timeout=15,
                )
                if res.status_code == 200:
                    st.session_state["audit_logs"] = res.json().get("logs", [])
                else:
                    show_api_error(res)
            except requests.RequestException:
                st.error(t("audit_connection_error"))

        if "audit_logs" in st.session_state:
            logs = st.session_state["audit_logs"]
            if logs:
                st.dataframe(localize_audit_logs(logs), use_container_width=True)
            else:
                st.info(t("no_logs"))
