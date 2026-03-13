"""
REST API Integration Demo
Demonstrates API key auth, error handling, pagination, and data export
"""
import requests
import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class RESTAPIClient:
    """Generic REST API client with authentication and error handling"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'API-Integration-Demo/1.0',
            'Accept': 'application/json'
        })
        
        if api_key:
            self.session.headers['Authorization'] = f'Bearer {api_key}'
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make GET request with error handling"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return {}
    
    def get_all_pages(self, endpoint: str, params: Optional[Dict] = None, 
                      max_pages: int = 5) -> List[Dict]:
        """Fetch paginated results"""
        all_results = []
        page = 1
        
        while page <= max_pages:
            page_params = {**(params or {}), 'page': page, 'per_page': 10}
            data = self.get(endpoint, page_params)
            
            if isinstance(data, list):
                results = data
            elif isinstance(data, dict):
                results = data.get('data', data.get('results', []))
            else:
                break
            
            if not results:
                break
                
            all_results.extend(results)
            print(f"✅ Page {page}: {len(results)} items")
            page += 1
        
        return all_results


class JSONPlaceholderDemo:
    """Demo using JSONPlaceholder (free fake API)"""
    
    def __init__(self):
        self.client = RESTAPIClient('https://jsonplaceholder.typicode.com')
    
    def get_posts(self, user_id: Optional[int] = None) -> List[Dict]:
        """Fetch posts with optional user filter"""
        params = {'userId': user_id} if user_id else None
        return self.client.get_all_pages('/posts', params)
    
    def get_user_details(self, user_id: int) -> Dict:
        """Fetch user details"""
        return self.client.get(f'/users/{user_id}')
    
    def get_comments_for_post(self, post_id: int) -> List[Dict]:
        """Fetch comments for a specific post"""
        return self.client.get(f'/posts/{post_id}/comments')
    
    def export_to_json(self, data: List[Dict], filename: str):
        """Export data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Exported to {filename}")


class GitHubAPIDemo:
    """Demo using GitHub API (requires token for higher rate limits)"""
    
    def __init__(self, token: Optional[str] = None):
        token = token or os.getenv('GITHUB_TOKEN')
        self.client = RESTAPIClient('https://api.github.com', token)
    
    def get_user_repos(self, username: str) -> List[Dict]:
        """Fetch user repositories"""
        repos = self.client.get_all_pages(f'/users/{username}/repos', max_pages=3)
        return [
            {
                'name': r['name'],
                'description': r['description'],
                'stars': r['stargazers_count'],
                'language': r['language'],
                'url': r['html_url']
            }
            for r in repos
        ]
    
    def get_repo_issues(self, owner: str, repo: str, state: str = 'open') -> List[Dict]:
        """Fetch repository issues"""
        return self.client.get_all_pages(
            f'/repos/{owner}/{repo}/issues',
            params={'state': state},
            max_pages=2
        )


def main():
    print("=" * 60)
    print("🌐 REST API Integration Demo")
    print("=" * 60)
    
    # Demo 1: JSONPlaceholder
    print("\n📋 Demo 1: JSONPlaceholder (Posts API)")
    print("-" * 40)
    
    demo = JSONPlaceholderDemo()
    
    # Get all posts
    posts = demo.get_posts()
    print(f"Total posts: {len(posts)}")
    
    # Get posts by specific user
    user_posts = demo.get_posts(user_id=1)
    print(f"Posts by user 1: {len(user_posts)}")
    
    # Get comments for first post
    if posts:
        comments = demo.get_comments_for_post(posts[0]['id'])
        print(f"Comments on post #{posts[0]['id']}: {len(comments)}")
    
    # Export sample data
    demo.export_to_json(user_posts[:5], 'sample_posts.json')
    
    # Demo 2: GitHub API (if token available)
    print("\n🐙 Demo 2: GitHub API")
    print("-" * 40)
    
    github = GitHubAPIDemo()
    
    try:
        repos = github.get_user_repos('octocat')
        print(f"Octocat's public repos: {len(repos)}")
        
        for repo in repos[:3]:
            print(f"  ⭐ {repo['name']}: {repo['stars']} stars ({repo['language'] or 'N/A'})")
    except Exception as e:
        print(f"⚠️ GitHub API error (maybe rate limited): {e}")
    
    print("\n✅ Demo completed!")


if __name__ == '__main__':
    main()
