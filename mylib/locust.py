from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    @task
    def load_page(self):
        self.client.get("/")
