
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

st.set_page_config(
    page_title="존중 그래프",
    page_icon="💚",
    layout="wide"
)

st.markdown("""
<style>
.stApp {background-color: #F7FAF7;}
h1, h2, h3 {color: #285943;}
[data-testid="stMetric"] {
    background: white;
    padding: 16px;
    border-radius: 12px;
    border: 1px solid #DDE9DF;
}
</style>
""", unsafe_allow_html=True)

st.title("💚 존중 그래프")
st.write("하루 동안 내가 얼마나 존중받았는지 기록하고 변화를 살펴봐요.")

if "records" not in st.session_state:
    st.session_state.records = []

menu = st.sidebar.radio(
    "메뉴",
    ["오늘 기록하기", "존중 그래프", "기록 모아보기"]
)

st.sidebar.info("점수는 다른 사람과 비교하기보다 나의 경험을 돌아보기 위한 기준이에요.")

if menu == "오늘 기록하기":
    st.header("오늘의 존중 기록")

    with st.form("record_form"):
        record_date = st.date_input("날짜", value=date.today())
        score = st.slider("오늘 존중받은 정도", 0, 10, 7)

        if score <= 2:
            label = "많이 아쉬웠어요"
        elif score <= 4:
            label = "조금 아쉬웠어요"
        elif score <= 6:
            label = "보통이었어요"
        elif score <= 8:
            label = "대체로 존중받았어요"
        else:
            label = "충분히 존중받았어요"

        st.subheader(f"{score}점 · {label}")

        factors = st.multiselect(
            "오늘 경험한 상황",
            [
                "내 의견을 들어줌",
                "말을 끊지 않고 경청함",
                "배려와 친절",
                "공정한 대우",
                "다름을 존중함",
                "무시하거나 비난하는 말",
                "의견을 표현하기 어려웠음"
            ]
        )

        memo = st.text_area(
            "기억에 남는 순간",
            placeholder="예: 친구가 내 의견을 끝까지 들어주었다.",
            max_chars=500
        )

        submitted = st.form_submit_button(
            "기록 저장",
            use_container_width=True
        )

    if submitted:
        st.session_state.records = [
            r for r in st.session_state.records
            if r["날짜"] != str(record_date)
        ]

        st.session_state.records.append({
            "날짜": str(record_date),
            "점수": score,
            "상황": ", ".join(factors),
            "메모": memo.strip()
        })

        st.session_state.records.sort(key=lambda r: r["날짜"])
        st.success("오늘의 기록을 저장했어요!")

        if score <= 3:
            st.info("불편했던 경험을 돌아보고, 필요하다면 믿을 수 있는 사람에게 이야기해 보세요.")
        elif score <= 6:
            st.info("존중을 느낀 순간과 아쉬웠던 순간을 함께 돌아보세요.")
        else:
            st.info("오늘의 좋은 경험을 기억하고 다른 사람에게도 존중을 실천해 보세요.")

elif menu == "존중 그래프":
    st.header("📈 나의 존중 변화")

    if not st.session_state.records:
        st.info("아직 기록이 없어요. 먼저 오늘의 기록을 작성해 주세요.")
    else:
        df = pd.DataFrame(st.session_state.records)
        df["날짜"] = pd.to_datetime(df["날짜"])
        df = df.sort_values("날짜")

        latest = df["날짜"].max().date()
        default_start = latest - timedelta(days=6)

        date_range = st.date_input(
            "조회 기간",
            value=(default_start, latest)
        )

        if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
            start, end = date_range
        else:
            start, end = df["날짜"].min().date(), latest

        if start > end:
            st.error("시작일은 종료일보다 늦을 수 없어요.")
        else:
            view = df[
                (df["날짜"].dt.date >= start)
                & (df["날짜"].dt.date <= end)
            ]

            if view.empty:
                st.warning("선택한 기간에 기록이 없어요.")
            else:
                c1, c2, c3 = st.columns(3)
                c1.metric("평균 점수", f"{view['점수'].mean():.1f}점")
                c2.metric("최고 점수", f"{view['점수'].max()}점")
                c3.metric("기록 일수", f"{len(view)}일")

                fig = px.line(
                    view,
                    x="날짜",
                    y="점수",
                    markers=True,
                    range_y=[0, 10],
                    title="날짜별 존중 점수",
                    hover_data=["상황", "메모"]
                )

                fig.update_traces(
                    line_color="#45A477",
                    line_width=3,
                    marker_size=9
                )
                fig.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    yaxis=dict(dtick=1, gridcolor="#E5EDE7"),
                    xaxis=dict(gridcolor="#EEF2EF")
                )

                st.plotly_chart(fig, use_container_width=True)

                st.caption(
                    "이 그래프는 기록한 개인의 경험을 보여 주며, "
                    "주변 전체의 존중 분위기를 객관적으로 측정하는 자료는 아니에요."
                )

else:
    st.header("📚 기록 모아보기")

    if not st.session_state.records:
        st.info("저장된 기록이 없어요.")
    else:
        df = pd.DataFrame(st.session_state.records)
        df = df.sort_values("날짜", ascending=False)

        st.dataframe(df, use_container_width=True, hide_index=True)

        st.download_button(
            "📥 CSV 파일 다운로드",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name="respect_records.csv",
            mime="text/csv"
        )

        selected = st.selectbox("삭제할 날짜", df["날짜"].tolist())

        if st.button("선택한 기록 삭제"):
            st.session_state.records = [
                r for r in st.session_state.records
                if r["날짜"] != selected
            ]
            st.success("기록을 삭제했어요.")
            st.rerun()

st.divider()
st.caption(
    "💚 존중은 서로의 의견을 듣고 차이를 인정하는 데서 시작됩니다. "
    "기록은 현재 세션에 저장되며, 세션이 종료되면 사라질 수 있어요."
)
