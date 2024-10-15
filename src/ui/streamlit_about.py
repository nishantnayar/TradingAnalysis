import streamlit as st
from PIL import Image


def streamlit_about_display():
    st.title('Author')
    with st.container():
        col1, col2 = st.columns([300, 100])
        col1.write('')
        col1.write('')
        col1.write('')
        col1.write('**Name:**   Nishant Nayar')
        col1.write('**Education:**    M.S. Data Science')
        col1.write('**College:**    Physical Sciences Division, University of Chicago')
        col1.write('**Contact:**    nishant.nayar@hotmail.com  or [linkedin](https://www.linkedin.com/in/nishantnayar)')
        img = Image.open(r"C:\Users\nisha\Documents\PythonProjects\TradingAnalysis\src\ui\fig\IMG_0245.jpg").resize(
            (200, 200))
        col2.image(img)

    st.title('About Me')
    st.write("Passionate about uncovering the potential within data, I bring over 15 years of experience in data "
             "management and analytics, complemented by an MS in Analytics from The University of Chicago with a "
             "focus on Data Visualization and Explainable AI. Throughout my career, I've successfully led agile "
             "development teams and orchestrated the execution of complex data programs, specializing in enterprise "
             "data management governance, technology, and strategy. With a track record of leading global teams and "
             "delivering business-critical projects, I thrive on the transformative power of data-driven "
             "decision-making. My commitment to optimizing operational efficiency and generating optimal business "
             "value through data analytics drives my professional journey.")
    st.title('Experience')
    st.markdown("- Vice President, JPMorganChase & Co., Chicago, New York")
    st.markdown("- Manager- Business Consulting, Sapient Corporation, Boston")
