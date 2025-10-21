from rest_framework.test import APITestCase
from rest_framework import status
from apps.projects.models import Project
from apps.startups.models import StartupProfile
from django.contrib.auth import get_user_model

User = get_user_model()

class ProjectPaginationTestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User"
        )
        
        self.startup = StartupProfile.objects.create(
            user=self.user,
            company_name="Test Startup",
            description="Test description",
            founded_year=2020,
            team_size=10,
            website="https://teststartup.com",
            email="contact@teststartup.com",
            phone="123456789",
            city="Test City",
            address="Test Address",
            postal_code="12345",
            logo="https://example.com/logo.jpg",
            partners_brands="Test Partners",
            audit_status="active"
        )
        
        for i in range(1, 16):
            Project.objects.create(
                title=f"Project {i}",
                slug=f"project-{i}",
                short_desc=f"Short description of Project {i}",
                description=f"Full description of Project {i}",
                status="in_progress",
                target_amount=100000.00,
                raised_amount=0.00,
                currency="UAH",
                thumbnail="https://example.com/image.jpg",
                tags="test, startup, project",
                visibility="public",
                startup=self.startup
            )

    def test_project_list_pagination_page_1(self):
        url = f'/api/startups/{self.startup.id}/projects/?page=1&page_size=6'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 6)  
        self.assertEqual(response.data['count'], 15)  
        
    def test_project_list_pagination_page_2(self):
        url = f'/api/startups/{self.startup.id}/projects/?page=2&page_size=6'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 6)  
        self.assertEqual(response.data['count'], 15)  

    def test_project_list_pagination_page_3(self):
        url = f'/api/startups/{self.startup.id}/projects/?page=3&page_size=6'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  
        self.assertEqual(response.data['count'], 15)  

    def test_project_list_pagination_invalid_page(self):
        url = f'/api/startups/{self.startup.id}/projects/?page=4&page_size=6'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 