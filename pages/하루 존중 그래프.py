
import streamlit as st
import csv
import io
from datetime import date, timedelta

# 기본 설정
st.set_page_config(
    page_title="하루 존중 그래프",
    page_icon="💚",
    layout="wide"
)

# 디자인
st.markdown("""
<style>
.stApp {
    background-color: #F7FAF8;
}
.main-title {
    background: linear-gradient(120deg, #DDF3E4, #EAF5F0);
    padding: 25px;
    border-radius: 18px;
    margin-bottom: 20px;
}
.main-title h1 {
    color: #285943;
}
.main-title p {
    color: #476B56;
}
div[data-testid="stMetric"] {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #DDE9DF;
}
</style>
""", unsafe_allow_html=True)

# 제목
st.markdown("""
<div class="main-title">
    <h1>💚 하루 존중 그래프</h1>
    <p>오늘 나는 얼마나 존중받았을까요?</p>
    <p>작은 경험을 기록하고 우리 주변의 존중 분위기를 돌아봐요.</p>
</div>
""", unsafe_allow_html=True)

# 기록 저장
if "records" not in st.session_state:
    st.session_state.records = []

# 메뉴
menu = st.sidebar.radio(
    "메뉴 선택",
    ["오늘의 존중 기록", "존중 그래프", "기록 모아보기"]
)

st.sidebar.markdown("---")
st.sidebar.caption("나의 경험을 기록하는 공간입니다.")

# --------------------------------
# 1. 오늘의 존중 기록
# --------------------------------

if menu == "오늘의 존중 기록":

    st.header("📝 오늘의 존중 기록")
    st.write("오늘 하루를 떠올리며 솔직하게 평가해 보세요.")

    with st.form("respect_form"):

        selected_date = st.date_input(
            "기록 날짜",
            value=date.today()
        )

        score = st.slider(
            "오늘 존중받은 정도",
            min_value=0,
            max_value=10,
            value=7
        )

        if score <= 2:
            message = "존중이 많이 부족했다고 느낀 하루"
        elif score <= 4:
            message = "아쉬운 순간이 있었던 하루"
        elif score <= 6:
            message = "평범한 하루"
        elif score <= 8:
            message = "대체로 존중받은 하루"
        else:
            message = "충분히 존중받은 하루"

        st.subheader(f"{score}점 / 10점")
        st.info(message)

        experiences = st.multiselect(
            "오늘 경험한 존중의 모습",
            [
                "내 의견을 존중해 줌",
                "내 말을 끝까지 들어 줌",
                "친절하게 대해 줌",
                "공평하게 대우해 줌",
                "서로의 차이를 인정해 줌",
                "나를 무시하거나 비난함",
                "의견을 자유롭게 표현하기 어려웠음"
            ]
        )

        memo = st.text_area(
            "오늘 기억에 남는 상황",
            placeholder="오늘 어떤 일이 있었나요?",
            max_chars=500
        )

        save = st.form_submit_button(
            "💚 기록 저장하기",
            use_container_width=True
        )

    if save:

        date_text = selected_date.isoformat()

        new_record = {
            "날짜": date_text,
            "점수": score,
            "경험": ", ".join(experiences),
            "메모": memo.strip()
        }

        # 같은 날짜의 기록은 덮어쓰기
        st.session_state.records = [
            r for r in st.session_state.records
            if r["날짜"] != date_text
        ]

        st.session_state.records.append(new_record)

        st.session_state.records.sort(
            key=lambda x: x["날짜"]
        )

        st.success("오늘의 존중 기록이 저장되었습니다!")

        if score <= 3:
            st.write(
                "오늘의 경험을 돌아보고 필요한 경우 "
                "믿을 수 있는 사람에게 이야기해 보세요."
            )
        elif score <= 6:
            st.write(
                "존중받았던 순간과 아쉬웠던 순간을 "
                "함께 생각해 보세요."
            )
        else:
            st.write(
                "오늘 느낀 좋은 존중의 경험을 "
                "다른 사람에게도 실천해 보세요."
            )

# --------------------------------
# 2. 존중 그래프
# --------------------------------

elif menu == "존중 그래프":

    st.header("📊 나의 존중 그래프")

    records = st.session_state.records

    if len(records) == 0:

        st.info(
            "아직 기록이 없습니다. "
            "먼저 오늘의 존중 기록을 작성해 주세요."
        )

    else:

        sorted_records = sorted(
            records,
            key=lambda x: x["날짜"]
        )

        latest = date.fromisoformat(
            sorted_records[-1]["날짜"]
        )

        start_default = latest - timedelta(days=6)

        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input(
                "시작 날짜",
                value=start_default,
                key="start_date"
            )

        with col2:
            end_date = st.date_input(
                "종료 날짜",
                value=latest,
                key="end_date"
            )

        if start_date > end_date:

            st.error("시작 날짜를 종료 날짜보다 빠르게 설정해 주세요.")

        else:

            filtered = [
                r for r in sorted_records
                if start_date.isoformat()
                <= r["날짜"]
                <= end_date.isoformat()
            ]

            if len(filtered) == 0:

                st.warning("선택한 기간에 기록이 없습니다.")

            else:

                scores = [
                    int(r["점수"])
                    for r in filtered
                ]

                dates = [
                    r["날짜"]
                    for r in filtered
                ]

                average = sum(scores) / len(scores)
                highest = max(scores)
                lowest = min(scores)

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "평균 존중 점수",
                    f"{average:.1f}점"
                )

                c2.metric(
                    "최고 점수",
                    f"{highest}점"
                )

                c3.metric(
                    "기록한 날짜",
                    f"{len(scores)}일"
                )

                st.markdown("---")
                st.subheader("📈 날짜별 존중 변화")

                chart_data = {
                    "날짜": dates,
                    "존중 점수": scores
                }

                st.line_chart(
                    chart_data,
                    x="날짜",
                    y="존중 점수"
                )

                st.caption(
                    "점수가 높을수록 존중받았다고 느낀 정도가 높습니다."
                )

                st.markdown("---")
                st.subheader("💬 기록 분석")

                if average >= 8:
                    st.success(
                        "전반적으로 존중을 많이 느낀 기간입니다."
                    )
                elif average >= 5:
                    st.info(
                        "존중을 느낀 순간과 아쉬운 순간이 함께 있었던 기간입니다."
                    )
                else:
                    st.warning(
                        "존중받는 분위기가 아쉽다고 느낀 기간입니다. "
                        "어떤 상황이 영향을 주었는지 돌아보세요."
                    )

                st.write(
                    f"가장 높은 점수: {highest}점"
                )
                st.write(
                    f"가장 낮은 점수: {lowest}점"
                )

# --------------------------------
# 3. 기록 모아보기
# --------------------------------

elif menu == "기록 모아보기":

    st.header("📚 나의 기록 모아보기")

    records = sorted(
        st.session_state.records,
        key=lambda x: x["날짜"],
        reverse=True
    )

    if len(records) == 0:

        st.info("아직 저장된 기록이 없습니다.")

    else:

        for record in records:

            with st.expander(
                f"{record['날짜']} | {record['점수']}점"
            ):

                st.write(
                    "**경험:**",
                    record["경험"] if record["경험"] else "입력 없음"
                )

                st.write(
                    "**메모:**",
                    record["메모"] if record["메모"] else "입력 없음"
                )

        st.markdown("---")

        st.subheader("📥 기록 다운로드")

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["날짜", "점수", "경험", "메모"]
        )

        writer.writeheader()
        writer.writerows(records)

        st.download_button(
            "CSV 파일 다운로드",
            data="\ufeff" + output.getvalue(),
            file_name="하루_존중_기록.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.markdown("---")
        st.subheader("🗑️ 기록 삭제")

        delete_date = st.selectbox(
            "삭제할 날짜 선택",
            [r["날짜"] for r in records]
        )

        confirm = st.checkbox(
            "선택한 기록을 삭제하겠습니다."
        )

        if st.button(
            "선택한 기록 삭제",
            disabled=not confirm
        ):

            st.session_state.records = [
                r for r in st.session_state.records
                if r["날짜"] != delete_date
            ]

            st.success("기록이 삭제되었습니다.")
            st.rerun()

# --------------------------------
# 하단 안내
# --------------------------------

st.markdown("---")

st.caption(
    "💚 존중은 서로의 의견을 듣고 차이를 인정하는 데서 시작됩니다."
)

st.caption(
    "※ 현재 기록은 앱 세션에 저장됩니다. "
    "세션이 종료되거나 서버가 재시작되면 기록이 사라질 수 있습니다."
)
