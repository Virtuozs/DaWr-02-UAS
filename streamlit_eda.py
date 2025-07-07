import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🛍️ Retail Store Sales - EDA Dashboard")

# === File Upload & Persistence ===
if "data_uploaded" not in st.session_state:
    uploaded_file = st.file_uploader("📂 Upload cleaned retail_store_sales.csv", type=["csv"])
    # if uploaded_file is not None:
    #     st.session_state.data_uploaded = True
    #     st.session_state.df = pd.read_csv(uploaded_file, parse_dates=["Transaction Date"])
    if uploaded_file is not None:
        st.session_state.data_uploaded = True
        st.session_state.df = pd.read_csv(uploaded_file, parse_dates=["Transaction Date"])
        st.rerun()
else:
    df = st.session_state.df

# === Once Uploaded ===
if "data_uploaded" in st.session_state:
    df = st.session_state.df
    df["Year"] = df["Transaction Date"].dt.year

    # === Sidebar Navigation ===
    st.sidebar.markdown("## 📂 Navigate")
    page = st.sidebar.radio("", [
        "Data",
        "Summary Statistics",
        "Sales Over Time",
        "Sales by Category",
        "Sales by Location",
        "Top 10 Items",
        "Category Trend",
        "Discount Trend"
    ])

    if page == "Data":
        st.subheader("📋 All Transaction Data with Pagination")
        rows_per_page = st.selectbox("Rows per page", [10, 25, 50, 100], index=0)
        total_rows = len(df)
        total_pages = (total_rows - 1) // rows_per_page + 1

        page_num = st.number_input("Page number", min_value=1, max_value=total_pages, value=1, step=1)
        start_idx = (page_num - 1) * rows_per_page
        end_idx = start_idx + rows_per_page

        st.write(f"Showing rows `{start_idx+1}` to `{min(end_idx, total_rows)}` of `{total_rows}`")
        st.dataframe(df.iloc[start_idx:end_idx])

    elif page == "Summary Statistics":
        st.subheader("📈 Summary Statistics")
        st.write(df.describe())

    elif page == "Sales Over Time":
        st.subheader("📅 Total Sales Over Time")
        location = st.multiselect("Select Location", df["Location"].unique(), default=[])
        show_all_years = st.checkbox("Show all years", value=True)
        years = sorted(df["Year"].unique())
        if not show_all_years:
            years = st.multiselect("Select Year", years, default=[])

        if location and (show_all_years or years):
            df_filtered = df[df["Location"].isin(location)]
            if not show_all_years:
                df_filtered = df_filtered[df_filtered["Year"].isin(years)]
            time_df = df_filtered.groupby("Transaction Date")["Total Spent"].sum().reset_index()
            fig = px.line(time_df, x="Transaction Date", y="Total Spent", title="Total Sales Over Time")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please select at least one location and year(s).")

    elif page == "Sales by Category":
        st.subheader("📊 Sales by Category")
        category = st.multiselect("Select Category", df["Category"].unique(), default=[])
        if category:
            df_filtered = df[df["Category"].isin(category)]
            cat_sales = df_filtered.groupby("Category")["Total Spent"].sum().sort_values(ascending=False)
            cat_sales_df = cat_sales.reset_index()
            cat_sales_df.columns = ["Category", "Total Sales"]
            fig = px.bar(cat_sales_df, x="Category", y="Total Sales")
            st.plotly_chart(fig)
        else:
            st.warning("Please select at least one category to view the chart.")

    elif page == "Sales by Location":
        st.subheader("🌍 Sales by Location")
        category = st.multiselect("Select Category", df["Category"].unique(), default=[])
        if category:
            df_filtered = df[df["Category"].isin(category)]
            loc_sales = df_filtered.groupby("Location")["Total Spent"].sum().sort_values(ascending=False)
            loc_sales_df = loc_sales.reset_index()
            loc_sales_df.columns = ["Location", "Total Sales"]
            fig = px.pie(loc_sales_df, names="Location", values="Total Sales",
                         title="Sales Distribution by Location")
            st.plotly_chart(fig)
        else:
            st.warning("Please select at least one category to view the chart.")

    elif page == "Top 10 Items":
        st.subheader("🏷️ Top 10 Items by Sales")
        location = st.multiselect("Select Location", df["Location"].unique(), default=[])
        if location:
            df_filtered = df[df["Location"].isin(location)]
            item_sales = df_filtered.groupby("Item")["Total Spent"].sum().sort_values(ascending=False).head(10)
            item_sales_df = item_sales.reset_index()
            item_sales_df.columns = ["Item", "Total Sales"]
            fig = px.bar(item_sales_df, x="Total Sales", y="Item", orientation="h")
            st.plotly_chart(fig)
        else:
            st.warning("Please select at least one location to view the chart.")

    elif page == "Category Trend":
        st.subheader("📈 Sales Trend by Category")
        location = st.multiselect("Select Location", df["Location"].unique(), default=[])
        show_all_years = st.checkbox("Show all years", value=True)
        years = sorted(df["Year"].unique())
        if not show_all_years:
            years = st.multiselect("Select Year", years, default=[])

        if location and (show_all_years or years):
            df_filtered = df[df["Location"].isin(location)]
            if not show_all_years:
                df_filtered = df_filtered[df_filtered["Year"].isin(years)]
            category_trend = df_filtered.groupby(["Transaction Date", "Category"])["Total Spent"].sum().reset_index()
            fig = px.line(category_trend, x="Transaction Date", y="Total Spent", color="Category",
                          title="Sales Over Time by Category")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please select at least one location and year(s).")

    elif page == "Discount Trend":
        st.subheader("📈 Sales Trend: Discount vs No Discount")
        location = st.multiselect("Select Location", df["Location"].unique(), default=[])
        show_all_years = st.checkbox("Show all years", value=True)
        years = sorted(df["Year"].unique())
        if not show_all_years:
            years = st.multiselect("Select Year", years, default=[])

        if location and (show_all_years or years):
            df_filtered = df[df["Location"].isin(location)]
            if not show_all_years:
                df_filtered = df_filtered[df_filtered["Year"].isin(years)]
            discount_trend = df_filtered.groupby(["Transaction Date", "Discount Applied"])["Total Spent"].sum().reset_index()
            fig = px.line(discount_trend, x="Transaction Date", y="Total Spent", color="Discount Applied",
                          title="Sales Over Time: Discount Applied vs Not Applied",
                          labels={"Discount Applied": "Discount Applied"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please select at least one location and year(s).")

    st.markdown("---")

else:
    st.info("📂 Please upload the cleaned CSV file to begin.")
