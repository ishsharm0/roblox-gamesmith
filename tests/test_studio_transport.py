import importlib.machinery
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

loader=importlib.machinery.SourceFileLoader("studio_transport",str(Path(__file__).resolve().parents[1]/"tools/studio"))
spec=importlib.util.spec_from_loader(loader.name,loader)
studio=importlib.util.module_from_spec(spec)
loader.exec_module(studio)
class Fake:
 def __init__(self,results): self.results=iter(results); self.calls=0
 def req(self,*args,**kwargs): self.calls+=1; return next(self.results)
class TransportTests(unittest.TestCase):
 def test_retries_undelivered_route_on_same_connection(self):
  error={"isError":True,"content":[{"type":"text","text":"Target is not reachable. No OnInvoke handler responded for this action."}]}
  success={"content":[{"type":"text","text":"ok"}]}
  m=Fake([error,success])
  with patch.object(studio.time,"sleep"):
   self.assertEqual(studio.call_with_transport_retry(m,"execute_luau",{}),success)
  self.assertEqual(m.calls,2)
 def test_never_retries_game_errors(self):
  error={"isError":True,"content":[{"type":"text","text":"assertion failed: wrong price"}]}
  m=Fake([error])
  self.assertEqual(studio.call_with_transport_retry(m,"execute_luau",{}),error)
  self.assertEqual(m.calls,1)
 def test_retry_is_bounded(self):
  error={"isError":True,"content":[{"type":"text","text":"Target is not reachable. No OnInvoke handler responded"}]}
  m=Fake([error]*3)
  with patch.object(studio.time,"sleep"):
   self.assertEqual(studio.call_with_transport_retry(m,"screen_capture",{}),error)
  self.assertEqual(m.calls,3)
