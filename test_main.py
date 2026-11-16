import ast,io,json,os,unittest
from pathlib import Path
from unittest.mock import patch
import main

class Tests(unittest.TestCase):
 def test_deterministic_and_only_picks_listed_move(self):
  f='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';m=['e2e4','d2d4','g1f3','b1c3']
  x=[main.choose(f,m) for _ in range(5)];self.assertEqual(len(set(x)),1);self.assertIn(x[0],m)
 def test_capture_promotion_en_passant_and_safety(self):
  self.assertEqual(main.choose('4k3/8/8/3q4/8/8/8/3RK3 w - - 0 1',['e1f1','d1d5']),'d1d5')
  self.assertEqual(main.choose('k7/4P3/8/8/8/8/8/4K3 w - - 0 1',['e7e8n','e7e8b','e7e8r','e7e8q']),'e7e8q')
  self.assertEqual(main.choose('k7/8/8/3pP3/8/8/8/7K w - d6 0 1',['e5e6','e5d6']),'e5d6')
  self.assertEqual(main.choose('r6k/8/8/8/8/8/8/R6K w - - 0 1',['a1a2','a1b1']),'a1b1')
 def test_environment_protocol_is_mocked_post_only_and_ordered(self):
  fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
  replies=[{'status':'your_move','game':7,'fen':fen,'legal_moves':['e2e4','d2d4']},{'status':'over'},{'status':'done','games':1,'wins':1,'draws':0,'losses':0}]
  seen=[]
  def fake(req):
   seen.append(req);return io.BytesIO(json.dumps(replies.pop(0)).encode())
  with patch.dict(os.environ,{'MAKEFUN_ENV_URL':'http://store:8080'}),patch.object(main.HTTP,'open',side_effect=fake):main.run()
  self.assertFalse(replies);self.assertEqual([r.full_url for r in seen],['http://store:8080/game','http://store:8080/move','http://store:8080/game'])
  self.assertTrue(all(r.get_method()=='POST' for r in seen))
  self.assertEqual(json.loads(seen[0].data),{})
  m=json.loads(seen[1].data);self.assertEqual(m['game'],7);self.assertIn(m['move'],['e2e4','d2d4'])
  self.assertEqual(json.loads(seen[2].data),{})
 def test_stdlib_imports_only_and_env_url_is_the_only_runner_origin(self):
  tree=ast.parse(Path('main.py').read_text());mods=set()
  for n in ast.walk(tree):
   if isinstance(n,ast.Import):mods|={a.name for a in n.names}
   elif isinstance(n,ast.ImportFrom) and n.module:mods.add(n.module)
  self.assertEqual(mods,{'json','os','sys','urllib.request'})
  src=Path('main.py').read_text();self.assertIn("os.environ.get('MAKEFUN_ENV_URL'",src);self.assertNotIn('MAKEFUN_SHOP_TOKEN',src)
 def test_empty_legal_list_fails(self):
  with self.assertRaises(ValueError):main.choose('8/8/8/8/8/8/8/8 w - - 0 1',[])

if __name__=='__main__':unittest.main()
