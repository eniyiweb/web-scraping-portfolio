"""
GraphQL API Integration Demo
Demonstrates GraphQL queries with GitHub's GraphQL API
"""
import requests
import json
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


class GraphQLClient:
    """Generic GraphQL client"""
    
    def __init__(self, endpoint: str, token: Optional[str] = None):
        self.endpoint = endpoint
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'GraphQL-Demo/1.0'
        }
        if token:
            self.headers['Authorization'] = f'Bearer {token}'
    
    def execute(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute GraphQL query"""
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        try:
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ GraphQL Error: {e}")
            return {'errors': [{'message': str(e)}]}


class GitHubGraphQLDemo:
    """GitHub GraphQL API demo"""
    
    def __init__(self, token: Optional[str] = None):
        token = token or os.getenv('GITHUB_TOKEN')
        self.client = GraphQLClient(
            'https://api.github.com/graphql',
            token
        )
    
    def get_user_info(self, username: str) -> Dict:
        """Fetch user profile information"""
        query = """
        query($username: String!) {
            user(login: $username) {
                name
                bio
                company
                location
                followers {
                    totalCount
                }
                following {
                    totalCount
                }
                repositories(privacy: PUBLIC, first: 10) {
                    totalCount
                    nodes {
                        name
                        description
                        stargazerCount
                        primaryLanguage {
                            name
                        }
                    }
                }
            }
        }
        """
        
        result = self.client.execute(query, {'username': username})
        
        if 'errors' in result:
            print(f"❌ Error: {result['errors']}")
            return {}
        
        return result.get('data', {}).get('user', {})
    
    def search_repositories(self, query: str, first: int = 10) -> List[Dict]:
        """Search repositories on GitHub"""
        search_query = """
        query($query: String!, $first: Int!) {
            search(query: $query, type: REPOSITORY, first: $first) {
                repositoryCount
                edges {
                    node {
                        ... on Repository {
                            name
                            owner {
                                login
                            }
                            description
                            stargazerCount
                            forkCount
                            primaryLanguage {
                                name
                            }
                        }
                    }
                }
            }
        }
        """
        
        result = self.client.execute(
            search_query, 
            {'query': query, 'first': first}
        )
        
        if 'errors' in result:
            print(f"❌ Error: {result['errors']}")
            return []
        
        search_data = result.get('data', {}).get('search', {})
        edges = search_data.get('edges', [])
        
        return [
            {
                'name': edge['node']['name'],
                'owner': edge['node']['owner']['login'],
                'description': edge['node']['description'],
                'stars': edge['node']['stargazerCount'],
                'forks': edge['node']['forkCount'],
                'language': edge['node']['primaryLanguage']['name'] if edge['node']['primaryLanguage'] else None
            }
            for edge in edges
        ]


def main():
    print("=" * 60)
    print("🚀 GraphQL API Integration Demo")
    print("=" * 60)
    
    github = GitHubGraphQLDemo()
    
    # Demo 1: Get user info
    print("\n👤 Demo 1: User Profile")
    print("-" * 40)
    
    user_info = github.get_user_info('octocat')
    
    if user_info:
        print(f"Name: {user_info.get('name', 'N/A')}")
        print(f"Bio: {user_info.get('bio', 'N/A')}")
        print(f"Followers: {user_info['followers']['totalCount']}")
        print(f"Public repos: {user_info['repositories']['totalCount']}")
    
    # Demo 2: Search repositories
    print("\n🔍 Demo 2: Repository Search")
    print("-" * 40)
    
    repos = github.search_repositories('web scraping python', first=5)
    
    print(f"Found {len(repos)} repositories:\n")
    for repo in repos:
        print(f"  📦 {repo['owner']}/{repo['name']}")
        print(f"     ⭐ {repo['stars']} | 🍴 {repo['forks']} | 📝 {repo['language'] or 'N/A'}")
        if repo['description']:
            print(f"     {repo['description'][:80]}...")
        print()
    
    print("✅ GraphQL demo completed!")


if __name__ == '__main__':
    main()
