import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정 및 한글 폰트 관련 안내
st.set_page_config(page_title="국민 영화관람 활성화 지원사업 데이터 시각화", layout="wide")

# 2. 데이터베이스 연결 확인
db_file = 'movie.db'

if not os.path.exists(db_file):
    st.error(f"❌ '{db_file}' 파일을 찾을 수 없습니다. 데이터베이스 파일이 같은 폴더에 있는지 확인해주세요!")
    st.stop()

def run_query(query):
    """SQL 쿼리를 실행하여 데이터프레임으로 반환하는 함수"""
    with sqlite3.connect(db_file) as conn:
        return pd.read_sql(query, conn)

# 헤더 부분
st.title("🎬 국민 영화관람 활성화 지원사업 데이터 시각화")
st.markdown("2025년 7월 25일부터 총 450만 장 배포되었던 영화 6천원 할인권의 효과를 시각화했습니다.")
st.divider()

# --- 차트 1: 주별 관객수 변화 ---
st.header("1. 주별 관객수 변화 추이")
sql1 = """
SELECT 
  substr(날짜,5,2) AS 월,
  ((CAST(substr(날짜,7,2) AS INTEGER)-1)/7 + 1) AS 주차,
  SUM(전체관객수) AS 총관객수
FROM daily_stats
GROUP BY 월, 주차
ORDER BY 월, 주차
"""
df1 = run_query(sql1)

df1['라벨'] = df1['월'].astype(int).astype(str) + '월 ' + df1['주차'].astype(int).astype(str) + '주차'

col1, col2 = st.columns([2, 1])
with col1:
    fig1 = px.line(df1, x='라벨', y='총관객수', title='주간 총 관객수 변화', markers=True)
    
    fig1.add_vline(
    x="7월 5주차",  # 실제 데이터 기준 맞춰야 함
    line_dash="dash",
    line_color="red"
)

    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🔍 분석 정보")
    st.code(sql1, language='sql')
    st.info("💡 **인사이트**\n- 할인권 배포 주차인 7월 5주에 주간 관객 수가 급증했습니다. \n- 주간 데이터의 등락이 반복되는 것은 할인권 배포 이전에도 나타나 외부 요인이 크다는 것을 시사합니다.")


# --- 차트 2: 정책 전 vs 후 평균 관객수 ---
st.header("2. 정책 시행 전/후 일평균 관객수 비교")
sql2 = """
SELECT 
  CASE 
    WHEN 날짜 >= '20250725' THEN '정책후'
    ELSE '정책전'
  END AS 정책여부,
  AVG(전체관객수) as 평균관객수,
  COUNT(*) AS 일수 
FROM daily_stats 
GROUP BY 정책여부
"""
df2 = run_query(sql2)

# 보기 좋게 순서 정렬 (정책전 -> 정책후)
df2['정책여부'] = pd.Categorical(df2['정책여부'], categories=['정책전', '정책후'], ordered=True)
df2 = df2.sort_values('정책여부')

col3, col4 = st.columns([2, 1])
with col3:
    fig2 = px.bar(
    df2, 
    x='정책여부', 
    y='평균관객수',
    color='정책여부',
    color_discrete_map={'정책전': '#AB63FA', '정책후': '#FFA15A'},
    title='정책 시행 전/후 평균 관객수 비교',
    text='평균관객수'
)

    fig2.update_traces(texttemplate='%{text:,.0f}', textposition='outside')

    fig2.update_layout(
    yaxis_title="평균 관객수 (명)"
    )

    fig2.update_yaxes(tickformat=",")

    st.plotly_chart(fig2, use_container_width=True)


with col4:
    st.subheader("🔍 분석 정보")
    st.code(sql2, language='sql')
    st.info("💡 **인사이트**\n- 정책 시행 이후 일평균 관객 수는 .\n- 막대의 높이 차이를 통해 정책의 직관적인 효과를 판단할 수 있습니다.")


# --- 차트 3: 한국 vs 외국 관객수 비교 ---
st.header("3. 한국 vs 외국 관객수 비교 (정책 기준)")
sql3 = """
SELECT 
  CASE 
    WHEN 날짜 >= '20250725' THEN '정책후'
    ELSE '정책전'
  END AS 정책여부,
  AVG(한국관객수) as 한국영화,
  AVG(외국관객수) as 외국영화
FROM daily_stats 
GROUP BY 정책여부
"""
df3 = run_query(sql3)

col5, col6 = st.columns([2, 1])
with col5:
    fig3 = go.Figure(data=[
        go.Bar(name='한국 영화 관객', x=df3['정책여부'], y=df3['한국영화'], marker_color='#1f77b4'),
        go.Bar(name='외국 영화 관객', x=df3['정책여부'], y=df3['외국영화'], marker_color='#ff7f0e')
    ])
    fig3.update_layout(barmode='group', title='정책별 한국/외국 관객 평균 비교')
    st.plotly_chart(fig3, use_container_width=True)

with col6:
    st.subheader("🔍 분석 정보")
    st.code(sql3, language='sql')
    st.info("💡 **인사이트**\n- 정책이 한국 영화와 외국 영화 중 어느 쪽에 더 큰 영향을 주었는지 비교 분석이 가능합니다.\n- 두 집단 간의 격차가 정책 후 좁혀졌는지 혹은 벌어졌는지 확인하세요.")

st.sidebar.success("데이터 분석 완료!")