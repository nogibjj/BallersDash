from locust import HttpUser, task


class StreamlitUser(HttpUser):
    @task
    def visit_homepage(self):
        self.client.get("/")  # Replace "/" with the URL of your Streamlit applications
