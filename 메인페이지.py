
import streamlit as st
from datetime import date, datetime
import csv
import io

st.set_page_config(
    page_title="교권 지킴이",
    page_icon="🛡️",
    layout="wide"
)

NAVY = "#16324F"
TEAL = "#167D75"

st.markdown(f"""
<style>
.stApp {{
    background: #F6F8FB;
}}
[data-testid="stSidebar"] {{
    background: {NAVY};
}}
[data-testid="stSidebar"] * {{
    color: white !important;
}}
.hero {{
    padding: 35px;
    border-radius: 20px;
    color: white;
    background: linear-gradient(120deg, {NAVY}, #245A70);
    margin-bottom: 20px;
}}
.hero h1 {{
    color: white;
    font-size: 2.7rem;
}}
.hero p {{
    color: #E6F2F7;
    font-size: 1.05rem;
}}
.feature {{
    background: white;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #E1E8EF;
    min-height: 160px;
}}
.feature h3 {{
    color: {NAVY};
}}
</style>
""", unsafe_allow_html=True)

if "records" not in st.session_state:
    st.session_state.records = []

st.sidebar.title("🛡️ 교권 지킴이")
st.sidebar.caption("존중하는 교실, 보호받는 교육활동")

page = st.sidebar.radio(
    "메뉴",
    [
        "메인페이지",
        "생활지도 기록",
        "기록 현황",
        "대응 가이드"
    ]
)

# 메인페이지
if page == "메인페이지":
    st.markdown("""
    <div class="hero">
        <p>EDUCATION · RESPECT · PROTECTION</p>
        <h1>🛡️ 교권 지킴이</h1>
        <h3>존중하는 교실, 보호받는 교육활동</h3>
        <p>
        생활지도 상황을 객관적으로 기록하고,
        학생과 교사가 함께 해결 방향을 찾도록 돕는 플랫폼입니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("교실의 갈등, 감정이 아닌 절차로 해결합니다.")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="feature">
        <h3>📝 사실 중심 기록</h3>
        상황과 지도 내용을 구체적으로 기록합니다.
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="feature">
        <h3>💬 공정한 피드백</h3>
        학생의 입장을 듣고 개선 방향을 찾습니다.
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="feature">
        <h3>🤝 함께 만드는 변화</h3>
        면담과 후속 점검으로 재발 방지를 돕습니다.
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.subheader("이용 절차")

    steps = st.columns(4)
    items = [
        ("01", "상황 기록", "관찰한 사실 기록"),
        ("02", "사실 확인", "학생의 설명 청취"),
        ("03", "피드백", "개선 계획 협의"),
        ("04", "후속 점검", "변화 확인")
    ]

    for col, item in zip(steps, items):
        with col:
            st.markdown(f"### {item[0]} · {item[1]}")
            st.caption(item[2])

    st.info(
        "교권 지킴이는 학생을 낙인찍기 위한 도구가 아닙니다. "
        "교사의 교육활동을 보호하고 교육적 해결을 돕는 것이 목적입니다."
    )

    st.subheader("바로 시작하기")

    left, right = st.columns(2)

    with left:
        if st.button("📝 생활지도 기록하기", use_container_width=True):
            st.session_state.open_record = True
            st.rerun()

    with right:
        if st.button("📊 기록 현황 확인하기", use_container_width=True):
            st.session_state.open_status = True
            st.rerun()

    if st.session_state.pop("open_record", False):
        st.info("왼쪽 메뉴에서 '생활지도 기록'을 선택하세요.")

    if st.session_state.pop("open_status", False):
        st.info("왼쪽 메뉴에서 '기록 현황'을 선택하세요.")


# 생활지도 기록
elif page == "생활지도 기록":
    st.title("📝 생활지도 상황 기록")
    st.write("추측이나 감정적인 표현보다 관찰한 사실을 중심으로 작성하세요.")

    with st.form("record_form"):
        incident_date = st.date_input(
            "발생 날짜",
            value=date.today()
        )

        class_name = st.text_input(
            "학급 / 수업",
            placeholder="예: 2학년 3반 수학"
        )

        category = st.selectbox(
            "상황 유형",
            [
                "지도 지시 불응",
                "반복적인 수업 방해",
                "무례한 언행",
                "지도에 대한 이견 표출",
                "기타"
            ]
        )

        observed = st.text_area(
            "관찰한 행동 및 상황 *",
            placeholder="실제로 관찰한 말과 행동을 구체적으로 적어 주세요."
        )

        guidance = st.text_area(
            "교사의 안내 및 지도 내용"
        )

        student_view = st.text_area(
            "학생의 설명 또는 입장"
        )

        response = st.selectbox(
            "당시 대응",
            [
                "구두 안내",
                "개별 대화",
                "수업 환경 조정",
                "보호자 소통",
                "학교 담당자와 협의",
                "기타"
            ]
        )

        followup = st.selectbox(
            "후속 조치",
            [
                "추가 관찰",
                "학생 면담 예정",
                "보호자와 소통 예정",
                "학교 담당자와 협의 예정",
                "후속 조치 완료",
                "아직 정하지 않음"
            ]
        )

        plan = st.text_area(
            "개선 계획 및 다음 단계"
        )

        confirmed = st.checkbox(
            "개인정보를 최소화하고 사실 중심으로 작성했습니다."
        )

        submitted = st.form_submit_button(
            "기록 저장",
            use_container_width=True
        )

    if submitted:
        if not observed.strip():
            st.error("관찰한 행동 및 상황을 입력해 주세요.")

        elif not confirmed:
            st.warning("기록 원칙 확인란에 체크해 주세요.")

        else:
            record = {
                "기록일시": datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                ),
                "발생날짜": incident_date.isoformat(),
                "학급/수업": class_name or "미입력",
                "상황유형": category,
                "관찰내용": observed,
                "지도내용": guidance,
                "학생입장": student_view,
                "당시대응": response,
                "후속조치": followup,
                "개선계획": plan
            }

            st.session_state.records.append(record)
            st.success("생활지도 기록이 저장되었습니다.")
            st.caption(
                "현재 기록은 실행 세션에 저장됩니다. "
                "세션 종료 시 사라질 수 있습니다."
            )


# 기록 현황
elif page == "기록 현황":
    st.title("📊 생활지도 기록 현황")

    records = st.session_state.records

    if not records:
        st.info("저장된 기록이 없습니다.")

    else:
        col1, col2, col3 = st.columns(3)

        col1.metric("전체 기록", f"{len(records)}건")

        completed = sum(
            r["후속조치"] == "후속 조치 완료"
            for r in records
        )

        col2.metric("후속 조치 완료", f"{completed}건")
        col3.metric(
            "추가 확인 필요",
            f"{len(records) - completed}건"
        )

        st.subheader("기록 목록")

        for i, record in enumerate(
            reversed(records), start=1
        ):
            title = (
                f"{record['발생날짜']} | "
                f"{record['상황유형']}"
            )

            with st.expander(title):
                st.write("**학급 / 수업**")
                st.write(record["학급/수업"])

                st.write("**관찰한 행동**")
                st.write(record["관찰내용"])

                st.write("**교사의 지도**")
                st.write(record["지도내용"] or "입력 없음")

                st.write("**학생의 입장**")
                st.write(record["학생입장"] or "입력 없음")

                st.write("**대응 및 후속 조치**")
                st.write(
                    f"{record['당시대응']} / "
                    f"{record['후속조치']}"
                )

                st.write("**개선 계획**")
                st.write(record["개선계획"] or "입력 없음")

        output = io.StringIO()
        fields = list(records[0].keys())

        writer = csv.DictWriter(
            output,
            fieldnames=fields
        )

        writer.writeheader()
        writer.writerows(records)

        st.download_button(
            "📥 기록 CSV 다운로드",
            data=output.getvalue().encode("utf-8-sig"),
            file_name="교권지킴이_기록.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.caption(
            "다운로드한 기록은 개인정보 보호 기준에 따라 안전하게 보관하세요."
        )


# 대응 가이드
elif page == "대응 가이드":
    st.title("🧭 생활지도 대응 가이드")

    st.write(
        "학생의 권리와 교사의 교육활동을 함께 존중하는 "
        "교육적 해결 절차를 안내합니다."
    )

    guides = [
        (
            "1. 상황 정리",
            "차분하게 기대 행동과 지도 이유를 안내하고 "
            "안전 문제가 있으면 학교 절차를 따릅니다."
        ),
        (
            "2. 사실 기록",
            "의도를 단정하지 말고 실제로 관찰한 행동과 "
            "상황을 구체적으로 기록합니다."
        ),
        (
            "3. 학생의 입장 듣기",
            "학생에게 자신의 생각과 행동의 이유를 "
            "설명할 기회를 제공합니다."
        ),
        (
            "4. 개선 목표 설정",
            "다음 수업에서 실천할 행동과 필요한 지원을 "
            "함께 검토합니다."
        ),
        (
            "5. 학교와 협력",
            "상황이 반복되면 학교 규정에 따라 관리자, "
            "상담 담당자, 보호자 등과 협의합니다."
        )
    ]

    for title, content in guides:
        with st.expander(title, expanded=True):
            st.write(content)

    st.warning(
        "이 앱은 공식 신고 시스템이나 법률 판단 도구가 아닙니다. "
        "긴급하거나 중대한 사안은 학교의 공식 절차를 이용하세요."
    )

st.markdown("---")
st.caption(
    "🛡️ 교권 지킴이 | 교육활동 보호와 상호 존중을 위한 시범 앱"
)
