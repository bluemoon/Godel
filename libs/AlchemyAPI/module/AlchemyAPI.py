
import urllib
import sys

from xml.dom.ext.reader import Sax2
from xml import xpath


class AlchemyAPI:
  _apiKey = ""
  _hostPrefix = "access"
  def setAPIHost(self, apiHost):
    self._hostPrefix = apiHost;
    if len(self._hostPrefix) < 2:
      raise 'Error setting API host.'
  def setAPIKey(self, apiKey):
    self._apiKey = apiKey;
    if len(self._apiKey) < 5:
      raise 'Error setting API key.'
  def loadAPIKey(self, filename):
    file = open(filename, 'r')
    line = file.readline()
    self._apiKey = line.strip();
    if len(self._apiKey) < 5:
      raise 'Error loading API key.'
  def URLGetTopRankedNamedEntity(self, url):
    self.CheckURL(url)
    return self.POST("URLGetTopRankedNamedEntity", "url", "url", url)
  def HTMLGetTopRankedNamedEntity(self, html, url):
    self.CheckHTML(html, url)
    return self.POSTHTML("HTMLGetTopRankedNamedEntity", "html", "html", html, url)
  def TextGetTopRankedNamedEntity(self, text):
    self.CheckText(text)
    return self.POST("TextGetTopRankedNamedEntity", "text", "text", text)
  def URLGetRankedNamedEntities(self, url):
    self.CheckURL(url)
    return self.POST("URLGetRankedNamedEntities", "url", "url", url)
  def HTMLGetRankedNamedEntities(self, html, url):
    self.CheckHTML(html, url)
    return self.POSTHTML("HTMLGetRankedNamedEntities", "html", "html", html, url)
  def TextGetRankedNamedEntities(self, text):
    self.CheckText(text)
    return self.POST("TextGetRankedNamedEntities", "text", "text", text)
  def URLGetNamedEntities(self, url):
    self.CheckURL(url)
    return self.POST("URLGetNamedEntities", "url", "url", url)
  def HTMLGetNamedEntities(self, html, url):
    self.CheckHTML(html, url)
    return self.POSTHTML("HTMLGetNamedEntities", "html", "html", html, url)
  def TextGetNamedEntities(self, text):
    self.CheckText(text)
    return self.POST("TextGetNamedEntities", "text", "text", text)
  def URLGetKeywords(self, url):
    self.CheckURL(url)
    return self.POST("URLGetKeywords", "url", "url", url)
  def HTMLGetKeywords(self, html, url):
    self.CheckHTML(html, url)
    return self.POSTHTML("HTMLGetKeywords", "html", "html", html, url)
  def TextGetKeywords(self, text):
    self.CheckText(text)
    return self.POST("TextGetKeywords", "text", "text", text)
  def URLGetLanguage(self, url):
    self.CheckURL(url)
    return self.POST("URLGetLanguage", "url", "url", url)
  def HTMLGetLanguage(self, html, url):
    self.CheckHTML(html, url)
    return self.POSTHTML("HTMLGetLanguage", "html", "html", html, url)
  def TextGetLanguage(self, text):
    self.CheckText(text)
    return self.POST("TextGetLanguage", "text", "text", text)
  def URLGetCategory(self, url):
    self.CheckURL(url)
    return self.POST("URLGetCategory", "url", "url", url)
  def HTMLGetCategory(self, html, url):
    self.CheckHTML(html, url)
    return self.POSTHTML("HTMLGetCategory", "html", "html", html, url)
  def URLGetText(self, url):
    self.CheckURL(url)
    return self.POST("URLGetText", "url", "url", url)
  def HTMLGetText(self, html, url):
    self.CheckHTML(html, url)
    return self.POSTHTML("HTMLGetText", "html", "html", html, url)
  def URLGetRawText(self, url):
    self.CheckURL(url)
    return self.POST("URLGetRawText", "url", "url", url)
  def HTMLGetRawText(self, html, url):
    self.CheckHTML(html, url)
    return self.POSTHTML("HTMLGetRawText", "html", "html", html, url)
  def URLGetTitle(self, url):
    self.CheckURL(url)
    return self.POST("URLGetTitle", "url", "url", url)
  def HTMLGetTitle(self, html, url):
    self.CheckHTML(html, url)
    return self.POSTHTML("HTMLGetTitle", "html", "html", html, url)
  def URLGetFeedLinks(self, url):
    self.CheckURL(url)
    return self.POST("URLGetFeedLinks", "url", "url", url)
  def HTMLGetFeedLinks(self, html, url):
    self.CheckHTML(html, url)
    return self.POSTHTML("HTMLGetFeedLinks", "html", "html", html, url)
  def URLGetMicroformats(self, url):
    self.CheckURL(url)
    return self.POST("URLGetMicroformatData", "url", "url", url)
  def HTMLGetMicroformats(self, html, url):
    self.CheckHTML(html, url)
    return self.POSTHTML("HTMLGetMicroformatData", "html", "html", html, url)
  def CheckText(self, text):
    if len(self._apiKey) < 5:
      raise 'Please load an API key.'
    if len(text) < 5:
      raise 'Please specify some text to analyze.'
  def CheckHTML(self, html, url):
    if len(self._apiKey) < 5:
      raise 'Please load an API key.'
    if len(html) < 10:
      raise 'Please specify a HTML document to analyze.'
    if len(url) < 10:
      raise 'Please specify a URL to analyze.'
  def CheckURL(self, url):
    if len(self._apiKey) < 5:
      raise 'Please load an API key.'
    if len(url) < 10:
      raise 'Please specify a URL to analyze.'
  def POSTHTML(self, apiCall, apiPrefix, argName, argData, url):
    endpoint = 'http://' + self._hostPrefix + '.alchemyapi.com/calls/' + apiPrefix + '/' + apiCall
    argText = 'apikey=' + self._apiKey + '&outputMode=xml&url=' + urllib.quote(url) + '&' + argName + '=' + urllib.quote(argData)
    handle = urllib.urlopen(endpoint, argText);
    result = handle.read();
    handle.close();
    reader = Sax2.Reader();
    doc = reader.fromString(result);
    nodes = xpath.Evaluate('/results/status', doc.documentElement);
    if nodes[0].firstChild.nodeValue != "OK":
      raise 'Error making API call.'
    return result
  def POST(self, apiCall, apiPrefix, argName, argData):
    endpoint = 'http://' + self._hostPrefix + '.alchemyapi.com/calls/' + apiPrefix + '/' + apiCall
    argText = 'apikey=' + self._apiKey + '&outputMode=xml&' + argName + '=' + urllib.quote(argData)
    handle = urllib.urlopen(endpoint, argText);
    result = handle.read();
    handle.close();
    reader = Sax2.Reader();
    doc = reader.fromString(result);
    nodes = xpath.Evaluate('/results/status', doc.documentElement);
    if nodes[0].firstChild.nodeValue != "OK":
      raise 'Error making API call.'
    return result



