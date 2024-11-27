import streamlit as st
import pandas as pd
import altair as alt

def compute_cps(P_i_list, C_i_list, A_i_list, N_s):
    # Validate input lengths
    if not (len(P_i_list) == len(C_i_list) == len(A_i_list)):
        raise ValueError("P_i_list, C_i_list, and A_i_list must be of the same length.")
    
    # Total Platform Costs
    total_platform_costs = sum(P_i_list)
    # Platform Costs per Search
    platform_costs_per_search = total_platform_costs / N_s

    # API Call Costs per Search
    api_call_costs_per_search = sum(C_i * A_i for C_i, A_i in zip(C_i_list, A_i_list))

    # Cost per Search (CPS)
    cps = platform_costs_per_search + api_call_costs_per_search

    return cps

def main():
    # Change the title color to purple
    title_html = "<h1 style='color: purple;'>Fuzzy Cost per Search (CPS)</h1>"
    st.markdown(title_html, unsafe_allow_html=True)

    st.write("by QD.")

    st.write("""
    This app calculates the **Cost per Search (CPS)** based on your platform costs and API usage.
    """)

    # Add the CPS equation
    st.latex(r"""
    \text{CPS} = \left( \frac{\sum_{i} P_i}{N_s} \right) + \left( \sum_{i} C_i \times A_i \right)
    """)

    # Add explanations of variables
    st.write("""
    **Variables:**

    - \( P_i \): Fixed cost for platform *i*
    - \( C_i \): Cost per API call for platform *i*
    - \( A_i \): Number of API calls per search for platform *i*
    - \( N_s \): Total number of searches
    """)

    # Sidebar Inputs
    st.sidebar.header("Input Parameters")
    N_s = st.sidebar.slider(
        "Total Number of Searches (N_s):",
        min_value=1,
        max_value=100000,
        value=5000,
        step=1
    )

    # Option to show CPS over a range of N_s
    show_cps_range = st.sidebar.checkbox("Show CPS over a range of Number of Searches (N_s)", value=True)
    if show_cps_range:
        N_s_min = st.sidebar.number_input("Minimum Number of Searches (N_s)", value=1000, step=100)
        N_s_max = st.sidebar.number_input("Maximum Number of Searches (N_s)", value=10000, step=100)
        N_s_step = st.sidebar.number_input("Number of Searches (N_s) Step Size", value=500, step=100)

    # Input Platform Data
    st.header("Platform Costs and API Usage")

    st.write("""
    Please enter the details for each platform below. You can add or remove platforms as needed.
    """)

    # Preloaded data for platforms
    default_data = {
        'Platform Name': [
            'Clarifai',
            'SerpAPI',
            'Supabase',
            'Expo',
            'AWS',
            'People Data Labs',
            'Endato (Teaser)',
            'Endato (Full)',
            'LaunchDarkly'
        ],
        'Fixed Cost (P_i)': [30, 75, 25, 100, 1, 100, 0, 0, 12],
        'Cost per API Call (C_i)': [0.0088, 0.02, 0, 0, 0, 0.25, 0.25, 0.25, 0],
        'API Calls per Search (A_i)': [2, 2, 0, 0, 0, 1, 1, 1, 0]
    }

    # Editable DataFrame
    platform_df = pd.DataFrame(default_data)
    edited_df = st.data_editor(platform_df, num_rows="dynamic")

    if edited_df.empty:
        st.error("Please enter at least one platform.")
        return

    # Extract data from DataFrame
    try:
        P_i_list = edited_df['Fixed Cost (P_i)'].astype(float).tolist()
        C_i_list = edited_df['Cost per API Call (C_i)'].astype(float).tolist()
        A_i_list = edited_df['API Calls per Search (A_i)'].astype(float).tolist()
        platform_names = edited_df['Platform Name'].tolist()
    except Exception as e:
        st.error(f"Error processing platform data: {e}")
        return

    # Display input parameters
    st.subheader("Input Parameters Summary:")
    st.write(f"**Total Number of Searches (N_s):** {N_s}")
    st.write("**Platform Details:**")
    st.dataframe(edited_df)

    # Compute CPS
    try:
        cps = compute_cps(P_i_list, C_i_list, A_i_list, N_s)

        # Display CPS with increased font size and purple color
        st.subheader("Cost per Search (CPS):")
        cps_html = f"""
        <p style='color: purple; font-size: 32px; font-weight: bold;'>${cps:.4f}</p>
        """
        st.markdown(cps_html, unsafe_allow_html=True)

        # Show CPS over a range of N_s with marker
        if show_cps_range:
            if N_s_min < N_s_max and N_s_step > 0:
                N_s_values = list(range(int(N_s_min), int(N_s_max) + 1, int(N_s_step)))
                cps_values = [compute_cps(P_i_list, C_i_list, A_i_list, N_s_val) for N_s_val in N_s_values]
                plot_data = pd.DataFrame({'Total Searches (N_s)': N_s_values, 'CPS ($)': cps_values})

                # Create Altair chart
                line_chart = alt.Chart(plot_data).mark_line().encode(
                    x=alt.X('Total Searches (N_s)', title='Total Number of Searches (N_s)'),
                    y=alt.Y('CPS ($)', title='Cost per Search (CPS) in dollars ($)'),
                    tooltip=['Total Searches (N_s)', 'CPS ($)']
                )

                # Create marker for current N_s and CPS
                current_point = pd.DataFrame({
                    'Total Searches (N_s)': [N_s],
                    'CPS ($)': [cps]
                })

                point_chart = alt.Chart(current_point).mark_circle(size=100, color='purple').encode(
                    x='Total Searches (N_s)',
                    y='CPS ($)',
                    tooltip=['Total Searches (N_s)', 'CPS ($)']
                )

                # Combine the line chart and the point
                combined_chart = (line_chart + point_chart).interactive()

                st.subheader("CPS Over a Range of Number of Searches (N_s)")
                st.altair_chart(combined_chart, use_container_width=True)

                # Add labels to the chart
                st.write("""
                **Chart Explanation:**
                - **X-axis:** Total Number of Searches (N_s)
                - **Y-axis:** Cost per Search (CPS) in dollars ($)
                - **Purple Marker:** Current CPS at the selected N_s
                """)
            else:
                st.error("Please ensure that Minimum N_s < Maximum N_s and N_s Step Size > 0.")
    except Exception as e:
        st.error(f"An error occurred during calculation: {e}")

if __name__ == '__main__':
    main()
