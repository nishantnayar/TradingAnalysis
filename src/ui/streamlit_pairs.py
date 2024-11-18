# -*- coding: utf-8 -*-
"""
Created on Sat Nov  2 18:32:47 2024

@author: nisha
"""

import streamlit as st
from streamlit_utils import load_correlation_data, load_yahoo_data
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder


def streamlit_pairs_trading_display():
    st.title('Pairs Trading')

    pairs_tab1, pairs_tab2, pairs_tab3 = st.tabs(
        ["Theory", "Analysis", "Pairs"])

    with pairs_tab1:
        st.header('Historical Perspective')
        st.markdown('This is where introduction will come')
        st.header('Introduction')
        st.markdown('This is where introduction will come')
        st.header('Basics')
        st.markdown('This is where introduction will come')
        st.subheader('Cointegration')
        st.subheader('Cointegration vs Correlation')
        st.header('Suggested Readings')

        st.markdown(
            """
        - Books
            - Pairs Tading - Quantitative Methods and Analysis - Ganapathy Vidyamurthy
        - Articles
            - Item 3
        - Videos
            - Video link
        """
        )

    with pairs_tab2:
        st.header('Data Ingestion')

        st.header('Data Enrichment')

        st.header('Checking for Cointegration')
        st.subheader('Engle-Granger Test')
        st.markdown('''The ***Engle-Granger*** test is a statistical method used to determine whether two (or more) time series are cointegrated. In pairs trading, this test helps identify pairs of stocks that have a long-term equilibrium relationship, meaning their prices tend to move together even if they diverge in the short term. Cointegration implies that a linear combination of the two series is stationary, which can be useful for building mean-reverting trading strategies.''')
        st.markdown('''
        - Step 1: Set up the time-series
            - start with two non-stationary time series. In our case we will take the log transformed closed prices.
            - The test assumes each series is individually integrated of order 1, or I(1), meaning each series has a unit root and is non-stationary.
        
        - Step 2: Run a regression between the two series
        - Step 3: Check residuals for stationarity
        ''')
        st.subheader('The Johansen Test')
        st.subheader('Correlation plot')

        coint_data_df = load_correlation_data()

        if coint_data_df is not None:

            color1 = '#f63366'
            gray = '#808080'
            # Create a custom colormap from white to the custom color
            custom_cmap = LinearSegmentedColormap.from_list(
                "custom_cmap", ["pink", color1])

            # Ensure p_value is of numeric type
            coint_data_df['ADF p-Value'] = pd.to_numeric(
                coint_data_df['ADF p-Value'], errors='coerce')

            # Pivot the DataFrame to create a matrix
            heatmap_data = coint_data_df.pivot(
                index='Asset 1', columns='Asset 2', values='ADF p-Value')

            # Create a mask for NaN values
            mask = heatmap_data.isna()

            # Fill NaN values with 0 or another placeholder if desired (optional)
            heatmap_data = heatmap_data.fillna(0)

            # Plot heatmap
            plt.figure(figsize=(10, 8))
            ax = sns.heatmap(
                heatmap_data,
                annot=True,
                cmap=custom_cmap,
                mask=mask,
                fmt=".5f",
                cbar=False
            )

            # Add gridlines
            ax.grid(True, which='major', color=gray,
                    linestyle=':', linewidth=0.5, zorder=1)
            ax.set_title("P-Value Heatmap for Asset Pairs",
                         fontsize=14, color=color1)
            # Add subtitle using text method
            # ax.text(0.5, 1.02, "Top 10", fontsize=10, color=color1, ha='center', va='center', transform=ax.transAxes)

            # Customize the dotted line appearance
            for line in ax.get_xgridlines() + ax.get_ygridlines():
                # Increase the space between dots (2 units of dash and 10 units of space)
                line.set_dashes((2, 10))

            # Set z-order of the heatmap to ensure it's above the gridlines
            for _, spine in ax.spines.items():
                spine.set_zorder(2)  # Heatmap spines on top of gridlines

            # Customize axis labels
            ax.set_ylabel('Asset 1', color=color1, fontsize=10)
            ax.set_xlabel('Asset 2', color=color1, fontsize=10)
            plt.xticks(rotation=0, fontsize=8)
            plt.yticks(rotation=0, fontsize=8)

            st.pyplot(plt)  # Use st.pyplot() to display the plot in Streamlit
        else:
            st.warning("No data available for correlation heatmap.")

        # Display Cointegrated pairs data

        # Store the DataFrame in session state for use in other parts of the app
        if 'coint_data_df' not in st.session_state:
            st.session_state['coint_data_df'] = coint_data_df

        # Display Cointegrated pairs data
        if not coint_data_df.empty:
            display = "<span style='color: red; font-weight: bold;'>Top 10 Cointegrated Pairs</span>"
            st.markdown(display, unsafe_allow_html=True)

            # Add a new column 'Pair' with values like Pair 1, Pair 2, etc.
            coint_data_df['Pair'] = [
                f"Pair {i+1}" for i in range(len(coint_data_df))]
            # coint_data_df['selection'] = ''

            # Reorder the columns to make 'Pair' the first column
            coint_data_df = coint_data_df[['Pair',
                                           'Asset 1', 'Asset 1 Long Name', 'Asset 1 Industry', 'Asset 1 Sector',
                                           'Asset 2', 'Asset 2 Long Name', 'Asset 2 Industry', 'Asset 2 Sector',
                                           'ADF p-Value']]

            # Options for AgGrid
            gb = GridOptionsBuilder.from_dataframe(coint_data_df)
            gb.configure_pagination(enabled=True, paginationPageSize=10)
            # Enable single row selection with a checkbox
            gb.configure_selection('single', use_checkbox=True)
            gridoptions_table = gb.build()

            # Display the table with AgGrid
            grid_response = AgGrid(coint_data_df, gridOptions=gridoptions_table,
                                   enable_enterprise_modules=True, use_container_width=True)

            # Get the selected row(s) (if any)
            selected_rows = grid_response['selected_rows']

            # Display selected_rows for debugging purposes
            # st.write("Selected rows:", selected_rows)
            selected_df = pd.DataFrame(selected_rows)
            # st.write(len(selected_df))

            if len(selected_df) == 0:
                st.warning('No row selected')
            else:
                # st.write('Row selected')
                asset_1_values = selected_df['Asset 1'].values[0]
                asset_1_long_name = selected_df['Asset 1 Long Name'].values[0]
                asset_2_values = selected_df['Asset 2'].values[0]
                selected_pair = selected_df['Pair'].values[0]
                asset_2_long_name = selected_df['Asset 2 Long Name'].values[0]
                # st.write("Selected Asset 1 values:", asset_1_values)

    with pairs_tab3:
        if len(selected_df) == 0:
            st.warning('No row selected')
        else:
            display = f"<span style='color: red; font-weight: bold;'>{selected_pair} selected with tickers {asset_1_values} and {asset_2_values}</span>"
            st.markdown(display, unsafe_allow_html=True)

            yahoo_data_df = load_yahoo_data()

            pairs_tab3_col1, pairs_tab3_col2 = st.columns(2)

            with pairs_tab3_col1:
                st.subheader(f"{asset_1_long_name} - {asset_1_values}")
                asset1_df = yahoo_data_df[yahoo_data_df['symbol']
                                          == asset_1_values]
                expander_heading1 = "**Key facts**"  # Simple Markdown bold
                with st.expander(expander_heading1, icon=":material/looks_one:"):
                    st.write(
                        f"**Long Name**: {asset1_df['longname'].values[0]}")
                    st.write(
                        f"**Short Name**: {asset1_df['shortname'].values[0]}")
                    st.write(
                        f"**Industry**: {asset1_df['industry'].values[0]}")
                    st.write(f"**Sector**: {asset1_df['sector'].values[0]}")
                    if not asset1_df['address2'].values[0]:
                        address = asset1_df['address1'].values[0] + ', ' + asset1_df['city'].values[0] + \
                            ', ' + asset1_df['state'].values[0] + ', ' + \
                            asset1_df['country'].values[0] + \
                            ', ' + asset1_df['zip'].values[0]

                    else:
                        address = asset1_df['address1'].values[0] + ', ' + asset1_df['address2'].values[0] + ', ' + asset1_df['city'].values[0] + \
                            ', ' + asset1_df['state'].values[0] + ', ' + \
                            asset1_df['country'].values[0] + \
                            ', ' + asset1_df['zip'].values[0]

                    st.write(f"***Address***: {address}")

                expander_heading2 = "**About Company**"  # Simple Markdown bold
                with st.expander(expander_heading2, icon=":material/looks_two:"):
                    st.write('**About**')
                    st.write(asset1_df['longbusinesssummary'].values[0])
                    url = asset1_df['website'].values[0]
                    st.write(f"**Company website**: [link]({url})")

            with pairs_tab3_col2:
                st.subheader(f"{asset_2_long_name} - {asset_2_values}")
