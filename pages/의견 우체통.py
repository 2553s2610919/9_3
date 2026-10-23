
import streamlit as st
import sqlite3
import hmac
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime, timezone

# ==========================================
# 1. 기본 설정
# ==========================================

st.set_page_config(
    page_title="마음이음 | 익명 소통함",
    page_icon="💌",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DB_PATH = Path(__file__).with_name("mindbridge.db")

TOPICS = [
    "생활지도 및 규칙",
    "말투와 의사소통",
    "상호 존중과 배려",
    "수업 및 학급 분위기",
    "기타 개선 의견",
]

STATUSES = ["접수", "검토 중", "해결 노력 중", "완료"]


# ==========================================
# 2. 디자인
# ==========================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #F8F9FC;
    }

    .block-container {
        max-width: 850px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #25334B;
    }

    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 800;
        color: #374785;
        margin-bottom: 8px;
    }

    .sub-title {
        text-align: center;
        color: #64748B;
        font-size: 1.02rem;
        margin-bottom: 25px;
    }

    .info-card {
        background: white;
        border: 1px solid #E3E8F0;
        border-radius: 16px;
        padding: 20px;
        margin: 14px 0;
    }

    .guide-card {
        background: #EEF3FF;
        border-left: 5px solid #7189D8;
        border-radius: 12px;
        padding: 18px;
        margin: 12px 0;
        color: #263756;
    }

    div.stButton > button[kind="primary"] {
        background-color: #5269B5;
        border-color: #5269B5;
        border-radius: 10px;
    }

    div[data-testid="stForm"] {
        background: white;
        border-radius: 15px;
        border: 1px solid #E4E9F2;
        padding: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# 3. 데이터베이스
# ==========================================

@contextmanager
def database():
    connection = sqlite3.connect(
        str(DB_PATH),
        timeout=15
    )
    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database():
    with database() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS opinions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                topic TEXT NOT NULL,
                situation TEXT NOT NULL,
                suggestion TEXT NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT '접수',
                public_text TEXT NOT NULL DEFAULT '',
                is_public INTEGER NOT NULL DEFAULT 0
            )
            """
        )


def save_opinion(role, topic, situation, suggestion):
    created_at = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d %H:%M UTC")

    with database() as conn:
        conn.execute(
            """
            INSERT INTO opinions
            (role, topic, situation, suggestion, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                role,
                topic,
                situation,
                suggestion,
                created_at,
            ),
        )


def get_opinions(public_only=False):
    with database() as conn:
        if public_only:
            rows = conn.execute(
                """
                SELECT *
                FROM opinions
                WHERE is_public = 1
                AND LENGTH(TRIM(public_text)) > 0
                ORDER BY id DESC
                """
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT *
                FROM opinions
                ORDER BY id DESC
                """
            ).fetchall()

        return [dict(row) for row in rows]


def update_opinion(
    opinion_id,
    status,
    public_text,
    is_public
):
    with database() as conn:
        conn.execute(
            """
            UPDATE opinions
            SET status = ?,
                public_text = ?,
                is_public = ?
            WHERE id = ?
            """,
            (
                status,
                public_text,
                int(is_public),
                opinion_id,
            ),
        )


def delete_opinion(opinion_id):
    with database() as conn:
        conn.execute(
            "DELETE FROM opinions WHERE id = ?",
            (opinion_id,),
        )


def get_admin_password():
    try:
        password = st.secrets.get(
            "ADMIN_PASSWORD", ""
        )
        return str(password).strip()
    except Exception:
        return ""


# ==========================================
# 4. 앱 시작
# ==========================================

try:
    initialize_database()
except Exception:
    st.error(
        "데이터 저장 공간을 준비하지 못했습니다. "
        "앱을 다시 실행하거나 관리자에게 문의해 주세요."
    )
    st.stop()


if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False


st.markdown(
    '<div class="main-title">💌 마음이음</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="sub-title">
        서로의 마음을 듣고, 존중으로 이어지는 우리 교실
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    "💡 이곳은 누군가를 비난하는 공간이 아니라, "
    "서로 불편했던 점을 이해하고 더 나은 교실을 "
    "만들기 위한 익명 소통 공간입니다."
)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "✍️ 의견 보내기",
        "💬 소통 게시판",
        "🌱 갈등 해결",
        "🔐 관리자",
    ]
)


# ==========================================
# 5. 익명 의견 작성
# ==========================================

with tab1:
    st.subheader("✍️ 마음을 전해주세요")

    st.write(
        "평소 말하기 어려웠던 생각을 "
        "익명으로 전달할 수 있습니다."
    )

    st.markdown(
        """
        <div class="info-card">
        <b>📮 마음이음 의견함 이용 약속</b>
        <p>
        ✅ 상대방을 존중하는 표현을 사용해 주세요.<br>
        ✅ 구체적인 상황과 개선 방법을 함께 적어 주세요.<br>
        ✅ 이름, 학번, 연락처 등 개인정보는 적지 마세요.<br>
        ✅ 비방, 욕설, 특정인에 대한 공격은 삼가 주세요.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("opinion_form", clear_on_submit=True):

        role = st.radio(
            "어떤 입장에서 의견을 작성하나요?",
            ["학생", "교사"],
            horizontal=True,
        )

        topic = st.selectbox(
            "어떤 주제인가요?",
            TOPICS,
        )

        if role == "학생":
            situation_placeholder = (
                "예: 생활지도를 받을 때 "
                "제 이야기를 충분히 설명하지 못해 "
                "아쉬웠던 경험이 있습니다."
            )
            suggestion_placeholder = (
                "예: 지적을 받은 이유를 이해하고 "
                "제 생각도 차분히 설명할 수 있는 "
                "기회가 있으면 좋겠습니다."
            )
        else:
            situation_placeholder = (
                "예: 생활지도 중 교사의 설명이 "
                "끝나기 전에 반박이 이어져 "
                "대화를 진행하기 어려운 경우가 있습니다."
            )
            suggestion_placeholder = (
                "예: 서로의 설명을 끝까지 듣고, "
                "의견이 다르더라도 존중하는 "
                "말투로 이야기하면 좋겠습니다."
            )

        situation = st.text_area(
            "어떤 점이 불편했나요?",
            placeholder=situation_placeholder,
            max_chars=600,
            height=140,
        )

        suggestion = st.text_area(
            "어떻게 개선되면 좋을까요?",
            placeholder=suggestion_placeholder,
            max_chars=600,
            height=140,
        )

        agreement = st.checkbox(
            "개인정보를 포함하지 않았으며, "
            "서로를 존중하는 표현으로 작성했습니다."
        )

        submitted = st.form_submit_button(
            "💌 익명 의견 전달하기",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        situation = situation.strip()
        suggestion = suggestion.strip()

        if len(situation) < 10:
            st.warning(
                "불편했던 상황을 10자 이상 작성해 주세요."
            )

        elif len(suggestion) < 10:
            st.warning(
                "개선 방법을 10자 이상 작성해 주세요."
            )

        elif not agreement:
            st.warning(
                "의견함 이용 약속을 확인해 주세요."
            )

        else:
            try:
                save_opinion(
                    role,
                    topic,
                    situation,
                    suggestion,
                )

                st.success(
                    "💌 의견이 익명으로 전달되었습니다!"
                )

                st.info(
                    "작성된 의견은 관리자가 검토합니다. "
                    "공개에 적합한 내용만 소통 게시판에 "
                    "게시될 수 있습니다."
                )

            except sqlite3.Error:
                st.error(
                    "의견을 저장하지 못했습니다. "
                    "잠시 후 다시 시도해 주세요."
                )

    st.caption(
        "이름이나 계정 정보는 입력받지 않습니다. "
        "단, 작성자의 학생·교사 신분을 확인하지는 "
        "않으며, 완전한 익명성이 보장되는 "
        "시스템은 아닙니다."
    )


# ==========================================
# 6. 공개 소통 게시판
# ==========================================

with tab2:
    st.subheader("💬 우리가 함께 만드는 교실")

    st.write(
        "관리자가 검토하고 공개한 의견을 확인해 보세요."
    )

    st.caption(
        "게시 내용은 익명 의견을 바탕으로 "
        "관리자가 정리한 문구입니다. "
        "제출자의 신분은 인증되지 않습니다."
    )

    try:
        public_opinions = get_opinions(
            public_only=True
        )

        if not public_opinions:
            st.info(
                "아직 공개된 의견이 없습니다. "
                "첫 번째 소통의 시작을 기다리고 있어요."
            )

        else:
            st.metric(
                "함께 나눈 의견",
                f"{len(public_opinions)}건",
            )

            for opinion in public_opinions:
                with st.container(border=True):
                    st.markdown(
                        f"#### 🌷 {opinion['topic']}"
                    )

                    st.caption(
                        f"의견 #{opinion['id']} "
                        f"· {opinion['created_at']} "
                        f"· {opinion['status']}"
                    )

                    # 사용자 입력을 HTML로 렌더링하지 않음
                    st.text(opinion["public_text"])

    except sqlite3.Error:
        st.error(
            "게시판을 불러오지 못했습니다."
        )


# ==========================================
# 7. 갈등 해결 가이드
# ==========================================

with tab3:
    st.subheader("🌱 존중하는 대화의 시작")

    st.write(
        "정당한 생활지도는 존중받아야 하며, "
        "학생의 의견 역시 차분하게 표현될 수 "
        "있어야 합니다."
    )

    st.markdown("### 🧑‍🎓 학생을 위한 대화 방법")

    st.markdown(
        """
        <div class="guide-card">
        <b>1. 먼저 설명을 끝까지 듣기</b><br>
        교사의 지도 이유를 먼저 이해하려고 노력합니다.
        </div>

        <div class="guide-card">
        <b>2. 감정보다 상황을 설명하기</b><br>
        "왜 저한테만 그래요?" 대신
        "어떤 점을 고쳐야 하는지 알고 싶어요."
        라고 표현합니다.
        </div>

        <div class="guide-card">
        <b>3. 개선할 행동을 구체적으로 정하기</b><br>
        같은 갈등이 반복되지 않도록
        실천할 수 있는 작은 행동부터 정합니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 👩‍🏫 교사를 위한 대화 방법")

    st.markdown(
        """
        <div class="guide-card">
        <b>1. 행동과 사람을 구분하기</b><br>
        학생의 인격이 아니라 개선이 필요한
        구체적인 행동을 설명합니다.
        </div>

        <div class="guide-card">
        <b>2. 학생의 생각을 들어보기</b><br>
        지도 취지를 설명한 뒤 학생의 입장도
        표현할 기회를 제공합니다.
        </div>

        <div class="guide-card">
        <b>3. 긍정적인 변화 인정하기</b><br>
        학생이 노력하거나 태도를 바꾼 경우
        구체적으로 격려합니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown("### 💭 이렇게 표현해 보세요")

    examples = {
        "생활지도에 불만이 생겼을 때": {
            "before": "왜 저한테만 뭐라고 하세요?",
            "after": (
                "제가 어떤 규칙을 지키지 못했는지 "
                "설명해 주시면 고치도록 노력하겠습니다."
            ),
        },
        "학생이 계속 반항할 때": {
            "before": "너는 왜 항상 말을 안 듣니?",
            "after": (
                "지금 대화가 잘 이어지지 않아 아쉽구나. "
                "서로의 말을 끝까지 들어보자."
            ),
        },
        "억울한 상황이 생겼을 때": {
            "before": "제 잘못도 아닌데 왜 그러세요?",
            "after": (
                "제가 알고 있는 상황이 조금 달라서 "
                "제 입장도 설명드리고 싶습니다."
            ),
        },
    }

    selected = st.selectbox(
        "갈등 상황을 선택해 보세요.",
        list(examples.keys()),
    )

    st.error(
        "❌ 갈등을 키울 수 있는 표현\n\n"
        + examples[selected]["before"]
    )

    st.success(
        "✅ 존중하는 표현\n\n"
        + examples[selected]["after"]
    )

    st.caption(
        "이 가이드는 일반적인 의사소통을 위한 "
        "자료입니다. 괴롭힘, 위협, 차별 등은 "
        "익명 게시판이 아닌 학교의 공식 상담·"
        "신고 절차를 이용해 주세요."
    )


# ==========================================
# 8. 관리자 페이지
# ==========================================

with tab4:
    st.subheader("🔐 의견함 관리자")

    admin_password = get_admin_password()

    if not admin_password:
        st.warning(
            "관리자 비밀번호가 설정되지 않았습니다. "
            "Streamlit Secrets에 ADMIN_PASSWORD를 "
            "등록해야 관리 기능을 사용할 수 있습니다."
        )

    else:
        if not st.session_state.admin_authenticated:

            with st.form("admin_login"):
                entered_password = st.text_input(
                    "관리자 비밀번호",
                    type="password",
                )

                login = st.form_submit_button(
                    "관리자 로그인",
                    type="primary",
                )

            if login:
                if hmac.compare_digest(
                    entered_password,
                    admin_password,
                ):
                    st.session_state.admin_authenticated = True
                    st.rerun()
                else:
                    st.error(
                        "비밀번호가 올바르지 않습니다."
                    )

        else:
            st.success("관리자 모드입니다.")

            if st.button("🚪 로그아웃"):
                st.session_state.admin_authenticated = False
                st.rerun()

            try:
                all_opinions = get_opinions()

                total = len(all_opinions)

                completed = sum(
                    1 for opinion in all_opinions
                    if opinion["status"] == "완료"
                )

                reviewing = sum(
                    1 for opinion in all_opinions
                    if opinion["status"]
                    in ["검토 중", "해결 노력 중"]
                )

                col1, col2, col3 = st.columns(3)

                col1.metric("전체 의견", total)
                col2.metric("진행 중", reviewing)
                col3.metric("완료", completed)

                st.divider()

                filter_status = st.selectbox(
                    "처리 상태별 보기",
                    ["전체"] + STATUSES,
                )

                if filter_status == "전체":
                    filtered = all_opinions
                else:
                    filtered = [
                        opinion
                        for opinion in all_opinions
                        if opinion["status"] == filter_status
                    ]

                if not filtered:
                    st.info(
                        "해당하는 의견이 없습니다."
                    )

                for opinion in filtered:

                    opinion_id = opinion["id"]

                    with st.expander(
                        f"#{opinion_id} · "
                        f"{opinion['topic']} · "
                        f"{opinion['status']}"
                    ):

                        st.write(
                            "**작성 시 선택한 입장:** "
                            + opinion["role"]
                            + " (미인증)"
                        )

                        st.caption(
                            opinion["created_at"]
                        )

                        st.markdown(
                            "**불편했던 상황**"
                        )
                        st.text(
                            opinion["situation"]
                        )

                        st.markdown(
                            "**제안한 개선 방법**"
                        )
                        st.text(
                            opinion["suggestion"]
                        )

                        with st.form(
                            f"manage_form_{opinion_id}"
                        ):

                            current_status = (
                                opinion["status"]
                                if opinion["status"] in STATUSES
                                else "접수"
                            )

                            status = st.selectbox(
                                "처리 상태",
                                STATUSES,
                                index=STATUSES.index(
                                    current_status
                                ),
                            )

                            public_text = st.text_area(
                                "공개 게시판에 올릴 문구",
                                value=opinion["public_text"],
                                max_chars=1000,
                                height=130,
                                help=(
                                    "원문을 그대로 공개하지 말고 "
                                    "개인정보나 특정인을 알아볼 "
                                    "수 있는 표현을 제거해 주세요."
                                ),
                            )

                            is_public = st.checkbox(
                                "이 문구를 게시판에 공개",
                                value=bool(
                                    opinion["is_public"]
                                ),
                            )

                            save_changes = (
                                st.form_submit_button(
                                    "💾 변경 사항 저장",
                                    type="primary",
                                )
                            )

                        if save_changes:
                            clean_text = public_text.strip()

                            if (
                                is_public
                                and not clean_text
                            ):
                                st.warning(
                                    "의견을 공개하려면 "
                                    "공개 문구를 입력해 주세요."
                                )

                            else:
                                try:
                                    update_opinion(
                                        opinion_id,
                                        status,
                                        clean_text,
                                        is_public,
                                    )
                                    st.success(
                                        "변경 사항이 저장되었습니다."
                                    )
                                    st.rerun()

                                except sqlite3.Error:
                                    st.error(
                                        "변경 사항을 저장하지 "
                                        "못했습니다."
                                    )

                        st.divider()

                        confirm_delete = st.checkbox(
                            "삭제 확인",
                            key=f"confirm_{opinion_id}",
                        )

                        if st.button(
                            "🗑️ 의견 영구 삭제",
                            key=f"delete_{opinion_id}",
                            disabled=not confirm_delete,
                        ):
                            try:
                                delete_opinion(
                                    opinion_id
                                )
                                st.rerun()

                            except sqlite3.Error:
                                st.error(
                                    "의견을 삭제하지 못했습니다."
                                )

            except sqlite3.Error:
                st.error(
                    "관리자 데이터를 불러오지 못했습니다."
                )


# ==========================================
# 9. 하단 안내
# ==========================================

st.divider()

st.markdown(
    """
    <div style="
        text-align:center;
        color:#8490A3;
        font-size:13px;
        padding:12px;
    ">
        💌 마음이음 | 서로를 존중하는 교실 만들기<br>
        우리의 작은 대화가 더 나은 교실을 만듭니다.
    </div>
    """,
    unsafe_allow_html=True,
)
