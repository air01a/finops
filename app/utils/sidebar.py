from datetime import  timedelta


def show_side_bar(st,start_date, end_date):

    st.sidebar.header("Input Parameters")
    start_date = st.sidebar.date_input("Start Date", start_date,format="DD/MM/YYYY") 
    end_date = st.sidebar.slider("Sélectionnez le range de jours:",
                           value=14,
                           min_value=1,
                           max_value=14)

    return (start_date, start_date + timedelta(days=end_date))