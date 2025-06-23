"""
Project-S Web Tools
-----------------
Ez a modul a webes műveletekhez kapcsolódó eszközöket tartalmazza:
- Weboldal letöltés és tartalom kinyerés
- Webes keresés
- API hívás végrehajtás
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Union
import httpx
import re
import urllib.parse
from bs4 import BeautifulSoup
import ssl

from tools.tool_interface import BaseTool
from tools.tool_registry import tool_registry

logger = logging.getLogger(__name__)

class WebPageFetchTool(BaseTool):
    """
    Weboldal letöltése és tartalom kinyerése.
    
    Category: web
    Version: 1.0.0
    Requires permissions: Yes
    Safe: Yes
    """
    
    async def execute(self, 
                    url: str, 
                    extract_text: bool = True,
                    timeout: int = 10,
                    headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Letölt egy weboldalt és visszaadja a tartalmát.
        
        Args:
            url: A weboldal URL-je
            extract_text: Ha True, kinyeri a szöveges tartalmat a HTML-ből
            timeout: Időtúllépés másodpercben
            headers: Opcionális HTTP fejlécek
            
        Returns:
            Dict: Az eredmény szótár formában
        """
        try:
            # URL ellenőrzés
            if not url.startswith(("http://", "https://")):
                return {
                    "success": False,
                    "error": f"Érvénytelen URL: {url} - Az URL-nek http:// vagy https://-sel kell kezdődnie"
                }
                
            # Domainnév kinyerése biztonsági ellenőrzéshez
            domain = urllib.parse.urlparse(url).netloc
                
            # Biztonsági ellenőrzés
            security_check = tool_registry.check_security("network_access", {"domain": domain})
            if not security_check["allowed"]:
                return {
                    "success": False,
                    "error": security_check["reason"]
                }
                
            # Alapértelmezett fejlécek
            default_headers = {
                "User-Agent": "Project-S Agent/1.0 (compatible; ModernWebKit)"
            }
            
            # Fejlécek egyesítése, ha vannak megadva egyedi fejlécek
            if headers:
                default_headers.update(headers)
                
            # Weboldal letöltése
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=default_headers)
                
                # Státusz kód ellenőrzés
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"A kérés sikertelen, státusz kód: {response.status_code}",
                        "status_code": response.status_code
                    }
                    
                # Szöveges tartalom kinyerése, ha kérték
                text_content = None
                if extract_text:
                    # HTML elemzés BeautifulSoup-pal
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    # Script és stílus elemek eltávolítása
                    for script_or_style in soup(["script", "style"]):
                        script_or_style.extract()
                        
                    # Szöveges tartalom kinyerése
                    text_content = soup.get_text(separator='\n', strip=True)
                    
                # Metaadatok kinyerése
                title = None
                description = None
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Cím keresése
                title_tag = soup.find("title")
                if title_tag:
                    title = title_tag.text.strip()
                    
                # Leírás keresése
                meta_desc = soup.find("meta", attrs={"name": "description"})
                if meta_desc and meta_desc.get("content"):
                    description = meta_desc["content"].strip()
                    
                # Eredmény összeállítása
                result = {
                    "success": True,
                    "url": url,
                    "status_code": response.status_code,
                    "content_type": response.headers.get("Content-Type", "unknown"),
                    "title": title,
                    "description": description,
                    "html": response.text
                }
                
                if extract_text:
                    result["text"] = text_content
                    
                return result
                
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": f"Időtúllépés a weboldal letöltése közben: {url}"
            }
        except httpx.RequestError as e:
            return {
                "success": False,
                "error": f"Hiba a kérés végrehajtása közben: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Hiba a weboldal letöltése közben: {str(e)}")
            return {
                "success": False,
                "error": f"Hiba történt: {str(e)}"
            }


class WebApiCallTool(BaseTool):
    """
    HTTP API hívások végrehajtása.
    
    Category: web
    Version: 1.0.0
    Requires permissions: Yes
    Safe: Yes
    """
    
    async def execute(self, 
                    url: str, 
                    method: str = "GET",
                    headers: Optional[Dict[str, str]] = None,
                    data: Optional[Union[Dict[str, Any], str]] = None,
                    params: Optional[Dict[str, Any]] = None,
                    timeout: int = 10,
                    json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        HTTP API hívás végrehajtása.
        
        Args:
            url: Az API végpont URL-je
            method: HTTP metódus (GET, POST, PUT, DELETE, stb.)
            headers: HTTP fejlécek
            data: Küldendő adatok (form data vagy raw string)
            params: URL paraméterek
            timeout: Időtúllépés másodpercben
            json_data: JSON adat, ha van
            
        Returns:
            Dict: Az API hívás eredménye
        """
        try:
            # URL ellenőrzés
            if not url.startswith(("http://", "https://")):
                return {
                    "success": False,
                    "error": f"Érvénytelen URL: {url} - Az URL-nek http:// vagy https://-sel kell kezdődnie"
                }
                
            # HTTP metódus ellenőrzése
            method = method.upper()
            if method not in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]:
                return {
                    "success": False,
                    "error": f"Érvénytelen HTTP metódus: {method}"
                }
                
            # Domainnév kinyerése biztonsági ellenőrzéshez
            domain = urllib.parse.urlparse(url).netloc
                
            # Biztonsági ellenőrzés
            security_check = tool_registry.check_security("network_access", {"domain": domain})
            if not security_check["allowed"]:
                return {
                    "success": False,
                    "error": security_check["reason"]
                }
                
            # Alapértelmezett fejlécek
            default_headers = {
                "User-Agent": "Project-S Agent/1.0 (API Client)"
            }
            
            # Fejlécek egyesítése, ha vannak megadva egyedi fejlécek
            if headers:
                default_headers.update(headers)
                
            # API hívás végrehajtása
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                response = await client.request(
                    method=method, 
                    url=url, 
                    headers=default_headers,
                    params=params,
                    data=data,
                    json=json_data
                )
                
                # Eredmény összeállítása
                result = {
                    "success": True,
                    "url": url,
                    "method": method,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                }
                
                # Próbáljuk JSON-ként értelmezni, ha lehetséges
                try:
                    result["response"] = response.json()
                    result["content_type"] = "application/json"
                except json.JSONDecodeError:
                    result["response"] = response.text
                    result["content_type"] = response.headers.get("Content-Type", "text/plain")
                    
                return result
                
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": f"Időtúllépés az API hívás közben: {url}"
            }
        except httpx.RequestError as e:
            return {
                "success": False,
                "error": f"Hiba a kérés végrehajtása közben: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Hiba az API hívás közben: {str(e)}")
            return {
                "success": False,
                "error": f"Hiba történt: {str(e)}"
            }


class WebSearchTool(BaseTool):
    """
    Webes keresés végrehajtása (egyszerű).
    Ez a verzió nem használ külső API-t, csak egyszerű HTML elemzést.
    
    Category: web
    Version: 1.0.0
    Requires permissions: Yes
    Safe: Yes
    """
    
    async def execute(self, 
                    query: str, 
                    max_results: int = 5) -> Dict[str, Any]:
        """
        Webes keresés végrehajtása.
        
        Args:
            query: A keresési lekérdezés
            max_results: Maximálisan visszaadott találatok száma
            
        Returns:
            Dict: A keresési eredmények
        """
        try:
            # Lekérdezés URL-kódolása
            encoded_query = urllib.parse.quote_plus(query)
            
            # Összeállítjuk a keresési URL-t (egyszerű Google keresés)
            search_url = f"https://www.google.com/search?q={encoded_query}&num={max_results + 5}"
            
            # Biztonsági ellenőrzés
            security_check = tool_registry.check_security("network_access", {"domain": "www.google.com"})
            if not security_check["allowed"]:
                return {
                    "success": False,
                    "error": security_check["reason"]
                }
                
            # Fejlécek (böngésző utánzás)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5"
            }
            
            # Keresés végrehajtása
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                response = await client.get(search_url, headers=headers)
                
                # Státusz kód ellenőrzés
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"A keresési kérés sikertelen, státusz kód: {response.status_code}"
                    }
                    
                # HTML elemzés
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Keresési eredmények kinyerése
                search_results = []
                for result in soup.select("div.g"):
                    # Cím és URL kinyerése
                    title_element = result.select_one("h3")
                    link_element = result.select_one("a")
                    
                    if title_element and link_element and "href" in link_element.attrs:
                        link = link_element["href"]
                        
                        # Csak valódi linkek, nem Google belső linkek
                        if link.startswith("http") and "google.com" not in link:
                            # Leírás kinyerése
                            description = ""
                            desc_element = result.select_one("div.VwiC3b")
                            if desc_element:
                                description = desc_element.text.strip()
                                
                            search_results.append({
                                "title": title_element.text.strip(),
                                "url": link,
                                "description": description
                            })
                            
                            # Ha elérjük a maximális eredményszámot, kilépünk
                            if len(search_results) >= max_results:
                                break
                                
                return {
                    "success": True,
                    "query": query,
                    "results": search_results,
                    "count": len(search_results)
                }
                
        except Exception as e:
            logger.error(f"Hiba a webes keresés közben: {str(e)}")
            return {
                "success": False,
                "error": f"Hiba történt: {str(e)}"
            }


# Az eszközöket regisztráljuk a példányosításkor
web_page_fetch_tool = WebPageFetchTool()
web_api_call_tool = WebApiCallTool()
web_search_tool = WebSearchTool()

# Hozzáadjuk őket az exportált eszközökhöz
__all__ = ['web_page_fetch_tool', 'web_api_call_tool', 'web_search_tool']
