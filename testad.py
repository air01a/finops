import streamlit as st

from streamlit_azure_login import login_component
from os import environ

def login():
    with st.expander('Auth', expanded=True):
        token = login_component(
            header_text='Intercement', 
            authentication_endpoint_url=environ.get('-ca92-6671-86c1-56f936d25e36&protectedtoken=true&claims=%7b%22id_token%22%3a%7b%22xms_cc%22%3a%7b%22values%22%3a%5b%22CP1%22%5d%7d%7d%7d&domain_hint=damart.com&nonce=638420458841036865.96364c95-a716-4c80-9f40-9f3968226a41&state=FctBDoAgDAXRIvE4SKHl0x6HkLh16fWti3m7SUSUoyNKHNCEmHbWYaaNBYZxOQS6fZQ1G4pu4-K3_ojDesfSluI96_Ou-gE'), 
            logo_uri=environ.get('AD_LOGO_URI'),
            prefix=environ.get('.com'),
        )
        if token:
            return True
        
        return False

if __name__ == '__main__':
    st.set_page_config(layout="wide")

    # 1) We start the app without token and we set it to False
    if 'token' not in st.session_state:
        st.session_state.token = False
    
    # 3) We enter to the web logic
    if st.session_state.token:
        # Here goes the dashboard logic
        st.title('Test Azure Login')
    
    # 4) We create a logout button that re run the app
    if st.sidebar.button('Logout', key='logout_1'):
            del st.session_state['token']
            token = False
            st.session_state.token = False
            st.rerun()

    # 2) We make the login and set the token to True if the login goes ok 
    # or false if goes wrong
    else:
        token = login()
        st.session_state.token = token