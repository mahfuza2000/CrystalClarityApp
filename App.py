import streamlit as st
import pandas as pd
import altair as alt


st.set_page_config(page_title="Crystal Clear", page_icon="🌊")
st.title("Crystal Clear Water Quality Tracker")

st.write(
    """
    Investigate and compare local water quality data pulled from annual municiple water quality reports.
    """
)
st.divider()

@st.cache_data
def load_data():
    df = pd.read_csv("data/WaterQualityDatabase.csv")
    return df

df = load_data()
df['Year'] = df['Year'].astype(str)


mode = st.selectbox("Select Mode", ("Normal Mode", "Year Analysis Mode", "City Comparison Mode"))
st.divider()

if mode == "Normal Mode":

    years = st.slider("Year", 2021, 2023, (2021, 2023))

    cities = st.multiselect(
        "Select Cities to Display",
        df.City.unique(),
        ["Arlington", "Fort Worth", "Irving"],
    )

    contaminant = st.multiselect(
        "Contaminants to Filter",
        df.Contaminant.unique(),
        ["Arsenic", "Atrazine", "Barium", "Bromodichloromethane", "Bromofoam", 
        "Chloroform", "Chromiun", "Coliforms (fecal, E coli, etc)", "Copper", "Cyanide", 
        "Dibromochloromethane", "Fluoride", "Lead", "Nitrate", "Nitrite"]
    )

    st.write("\nAdditional Options\n")
    highlight_mcl = st.checkbox("Show Average Level > MCL Allowed", value=False)
    highlight_mclg = st.checkbox("Show Average Level > MCLG", value=False)

    if years:
        df = df[(df['Year'].astype(int) >= years[0]) & (df['Year'].astype(int) <= years[1])]

    if cities:
        df = df[df['City'].isin(cities)]

    if contaminant:
        df = df[df['Contaminant'].isin(contaminant)]

    def highlight_rows(row):
        if highlight_mcl and row['Average Level'] > row['MCL Allowed']:
            return ['background-color: #FF4D4D'] * len(row)
        elif highlight_mclg and row['Average Level'] > row['MCLG']:
            return ['background-color: #9999FF'] * len(row)
        return [''] * len(row)


    #st.subheader("Database of Municiple Water Quality")
    st.text("")
    st.markdown("<h2 style='text-align: center;'>Database of Municiple Water Quality</h2>", unsafe_allow_html=True)
    
    st.dataframe(df.style.apply(highlight_rows, axis=1), hide_index=True, use_container_width=True)
    # df.style.apply(highlight_rows, axis=1)
    # st.dataframe(df, hide_index=True, use_container_width=True)

    st.caption(
        """
        MCL: Maximum Contaminant Level Allowed (Regulated By Federal Government)\n
        MCLG: Maximum Contaminant Level Goal (Aspiring Target)
        """
    )

elif mode == "Year Analysis Mode":


    city = st.selectbox("Select City", df.City.unique())
    contaminants = st.multiselect("Select Contaminant", df['Contaminant'].unique())

    if  contaminants:
        df_analysis = df[(df['City'] == city) & (df['Contaminant'].isin(contaminants))]
    else:
        df_analysis = df[df['City'] == city]  

    st.text("")
    if not df_analysis.empty:
        chart_analysis = (
            alt.Chart(df_analysis)
            .mark_line()
            .encode(
                x=alt.X("Year:O", title="Year", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("Average Level:Q", title="Average Level (ppm/ppb)"),
                color=alt.Color("Contaminant:N", title="Contaminant"),
            )
            #.properties(title=f"Change in Average Level of Contaminants in {city} by Year", height=320)
            .properties(
                title={"text": ["Change in Average Level of Contaminants in {city} by Year"], "anchor": "middle"},  
                height=320
            )
        )

        st.altair_chart(chart_analysis, use_container_width=True)

elif mode == "City Comparison Mode":

    year = st.selectbox("Select Year", df['Year'].unique())
    contaminant = st.selectbox("Select Contaminant", df['Contaminant'].unique())

    df_comparison = df[(df['Year'] == year) & (df['Contaminant'] == contaminant)]

    st.text("")
    if not df_comparison.empty:
        histogram = (
            alt.Chart(df_comparison)
            .mark_bar()
            .encode(
                x=alt.X("City:N", title="City", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("Average Level:Q", title="Average Level (ppm/ppb)"),
                color=alt.Color("City:N", title="City", legend=None),
            )
            #.properties(title=f"Average Level of {contaminant} in {year} by City", height=320)
            .properties(
                title={"text": [f"Average Level of {contaminant} in {year} by City"], "anchor": "middle"},  
                height=320
            )
        )

        st.altair_chart(histogram, use_container_width=True)
