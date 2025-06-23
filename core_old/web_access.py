import aiohttp
import asyncio
import json
import os
import re
import subprocess
from typing import Dict, Any, Optional, List, Union
from bs4 import BeautifulSoup

class WebAccess:
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = None
        
    async def ensure_session(self):
        """Ensure an aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
            
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
            
    async def request(self, method: str, url: str, headers: Optional[Dict] = None, 
                      params: Optional[Dict] = None, data: Optional[Any] = None, 
                      json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make an HTTP request"""
        await self.ensure_session()
        
        for attempt in range(self.max_retries):
            try:
                async with self.session.request(
                    method, url, headers=headers, params=params, 
                    data=data, json=json_data
                ) as response:
                    
                    response_data = {
                        "status": response.status,
                        "headers": dict(response.headers),
                        "url": str(response.url)
                    }
                    
                    # Try to parse as JSON first
                    try:
                        response_data["json"] = await response.json()
                    except:
                        # If not JSON, get as text
                        response_data["text"] = await response.text()
                        
                    return response_data
                    
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == self.max_retries - 1:
                    return {
                        "error": str(e),
                        "status": None
                    }
                    
                # Wait before retrying
                await asyncio.sleep(1 * (attempt + 1))
                
    async def get(self, url: str, headers: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GET request"""
        return await self.request("GET", url, headers=headers, params=params)
        
    async def post(self, url: str, headers: Optional[Dict] = None, 
                  data: Optional[Any] = None, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a POST request"""
        return await self.request("POST", url, headers=headers, data=data, json_data=json_data)
        
    async def curl_request(self, command: str) -> Dict[str, Any]:
        """Execute a curl command and return the result"""
        # Split the command
        cmd_parts = command.split()
        if cmd_parts[0].lower() != "curl":
            cmd_parts.insert(0, "curl")
            
        # Add -s for silent mode if not present
        if "-s" not in cmd_parts:
            cmd_parts.insert(1, "-s")
            
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd_parts,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return {
                    "error": stderr.decode(),
                    "status": process.returncode
                }
                
            output = stdout.decode()
            
            # Try to parse as JSON
            try:
                return {
                    "json": json.loads(output),
                    "status": 200
                }
            except:
                return {
                    "text": output,
                    "status": 200
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "status": None
            }
            
    async def parse_html(self, html: str) -> Dict[str, Any]:
        """Parse HTML content and extract useful information"""
        soup = BeautifulSoup(html, 'html.parser')
        
        result = {
            "title": soup.title.string if soup.title else None,
            "text": soup.get_text(),
            "links": [{"text": a.text, "href": a.get("href")} for a in soup.find_all("a")],
            "headings": []
        }
        
        # Extract headings
        for tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            result["headings"].extend([
                {"level": int(tag[1]), "text": h.get_text()} 
                for h in soup.find_all(tag)
            ])
            
        # Extract meta tags
        result["meta"] = {
            meta.get("name", meta.get("property", "unknown")): meta.get("content")
            for meta in soup.find_all("meta") if meta.get("content")
        }
        
        return result
        
    async def extract_data(self, url: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extract data from a webpage using CSS selectors"""
        # Get the page
        response = await self.get(url)
        
        if "error" in response:
            return {"error": response["error"]}
            
        html = response.get("text", "")
        if not html:
            return {"error": "No HTML content found"}
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract data using the provided selectors
        result = {}
        for key, selector in selectors.items():
            elements = soup.select(selector)
            if elements:
                # If multiple elements, return a list
                if len(elements) > 1:
                    result[key] = [el.get_text().strip() for el in elements]
                else:
                    result[key] = elements[0].get_text().strip()
            else:
                result[key] = None
                
        return result