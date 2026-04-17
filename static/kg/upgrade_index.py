#!/usr/bin/env python3
"""
知识图谱 index.html 升级脚本
1. 用 KNOWLEDGE_DATA 替换硬编码的 D 变量
2. 添加 summaries.js 懒加载
3. 优化 D3 性能（限制节点数+加快收敛）
4. summary 字段改为懒加载
"""
import re

INDEX_HTML = "/home/admin/.openclaw/workspace/code-space/knowledge-graph/index.html"

with open(INDEX_HTML, "r", encoding="utf-8") as f:
    content = f.read()

# ========== 1. D = KNOWLEDGE_DATA ==========
# 找到 const D={...} 并替换为 const D=KNOWLEDGE_DATA;
old_d_pattern = r'const D=\{"nodes":\[.*?"links":\[.*?\]\};'
if re.search(old_d_pattern, content, re.DOTALL):
    content = re.sub(old_d_pattern, 'const D=KNOWLEDGE_DATA;', content, flags=re.DOTALL)
    print("✅ Replaced hardcoded D with KNOWLEDGE_DATA")
else:
    print("⚠️  D pattern not found, trying alternate...")
    # fallback: find the line and replace
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if line.strip().startswith('const D={"nodes"'):
            new_lines.append('const D=KNOWLEDGE_DATA;')
        else:
            new_lines.append(line)
    content = '\n'.join(new_lines)
    print("✅ Replaced D via line-by-line")

# ========== 2. 添加 SUMMARIES 懒加载变量和 summaries.js 动态加载 ==========
# 在 init() 函数前添加 SUMMARIES 变量声明和 summariesLoaded 标志
init_marker = "function init(){"
summaries_init = """let SUMMARIES={},summariesLoaded=false;
function loadSummaries(cb){
  if(summariesLoaded){cb();return;}
  var s=document.createElement('script');
  s.src='summaries.js';
  s.onload=function(){summariesLoaded=true;cb();};
  s.onerror=function(){cb();};
  document.head.appendChild(s);
}
"""

if 'let SUMMARIES={}' not in content:
    content = content.replace(init_marker, summaries_init + init_marker)
    print("✅ Added SUMMARIES lazy loading infrastructure")
else:
    print("⚠️  SUMMARIES already exists")

# ========== 3. 修改 fn() — 搜索不再依赖 n.summary ==========
# 原: n.label.toLowerCase().includes(sq)||n.summary.toLowerCase().includes(sq)
# 改: 只搜索 label (summary 是懒加载)
old_fn_search = r"n\.label\.toLowerCase\(\)\.includes\(sq\)\|\|n\.summary\.toLowerCase\(\)\.includes\(sq\)"
new_fn_search = "n.label.toLowerCase().includes(sq)"
if re.search(old_fn_search, content):
    content = re.sub(old_fn_search, new_fn_search, content)
    print("✅ Fixed fn() search (label-only)")
else:
    print("⚠️  fn() search pattern not found")

# ========== 4. 修改 renderGraph — 优化性能 ==========
# 4a: 降低 alphaDecay（更快收敛）
old_decay = "alphaDecay(.03)"
new_decay = "alphaDecay(.08)"
content = content.replace(old_decay, new_decay)

# 4b: 减少节点数限制（50→80）并优化
old_nodeslice = "const nc=nodes.slice(0,50).map(n=>({...n})),lc=links.map(l=>({...l}));"
new_nodeslice = "const nc=nodes.slice(0,80).map(n=>({...n})),lc=links.map(l=>({...l}));"
content = content.replace(old_nodeslice, new_nodeslice)

# 4c: 优化 forceManyBody strength（更弱的排斥力=更快的布局）
old_charge = "force('charge',d3.forceManyBody().strength(-200))"
new_charge = "force('charge',d3.forceManyBody().strength(-120))"
content = content.replace(old_charge, new_charge)

# 4d: 减少碰撞半径
old_collision = "force('collision',d3.forceCollide().radius(d=>Math.min(8+(d.connections||0)*2.5,26)+12))"
new_collision = "force('collision',d3.forceCollide().radius(d=>Math.min(8+(d.connections||0)*2.5,26)+8))"
content = content.replace(old_collision, new_collision)

print("✅ D3 performance optimizations applied")

# ========== 5. 修改 showDetail — 懒加载 summary ==========
# 原来的 showDetail 直接用 n.summary
# 改为先尝试 n.summary，没有则显示"点击加载"
old_showdetail = '''function showDetail(n){
  const color=CC[n.category]?.color||'#6B7280',emoji=CC[n.category]?.emoji||'📄';
  const related=[];
  D.links.forEach(l=>{const s=typeof l.source==='object'?l.source.id:l.source;const t=typeof l.target==='object'?l.target.id:l.target;if(s===n.id){const x=D.nodes.find(m=>m.id===t);if(x)related.push({node:x,rel:l.relation});}if(t===n.id){const x=D.nodes.find(m=>m.id===s);if(x)related.push({node:x,rel:l.relation});}});
  document.getElementById('detail-title').textContent=n.label;
  document.getElementById('detail-body').innerHTML=`<div class=detail-section><div class=detail-label>分类</div><span class=detail-category style=background:${color}>${emoji} ${n.category}</span></div><div class=detail-section><div class=detail-label>摘要</div><div class=detail-value>${n.summary}</div></div><div class=detail-section><div class=detail-label>来源</div><div class=detail-value>${n.source}</div></div><div class=detail-section><div class=detail-label>关联知识 (${related.length})</div>${related.length?`<div class=detail-relations>${related.map(r=>`<div class=relation-item onclick=jumpTo('${r.node.id}')><div class=relation-name>${r.node.label}</div><div class=relation-type>${r.rel}</div></div>`).join('')}</div>`:'<div class=detail-value>暂无关联</div>'}</div><div class=detail-section><a href=${n.url} target=_blank class=detail-url>🔗 查看归档原文</a></div>`;
  document.getElementById('detail').classList.add('open');
  hlG(n.id);
}'''

new_showdetail = '''function showDetail(n){
  const color=CC[n.category]?.color||'#6B7280',emoji=CC[n.category]?.emoji||'📄';
  const related=[];
  D.links.forEach(l=>{const s=typeof l.source==='object'?l.source.id:l.source;const t=typeof l.target==='object'?l.target.id:l.target;if(s===n.id){const x=D.nodes.find(m=>m.id===t);if(x)related.push({node:x,rel:l.relation});}if(t===n.id){const x=D.nodes.find(m=>m.id===s);if(x)related.push({node:x,rel:l.relation});}});
  const summary=n.summary||(SUMMARIES[n.id]||'（点击"查看归档原文"阅读完整摘要）');
  document.getElementById('detail-title').textContent=n.label;
  document.getElementById('detail-body').innerHTML=`<div class=detail-section><div class=detail-label>分类</div><span class=detail-category style=background:${color}>${emoji} ${n.category}</span></div><div class=detail-section><div class=detail-label>摘要</div><div class=detail-value id=detail-summary>${summary}</div></div><div class=detail-section><div class=detail-label>来源</div><div class=detail-value>${n.source}</div></div><div class=detail-section><div class=detail-label>关联知识 (${related.length})</div>${related.length?`<div class=detail-relations>${related.map(r=>`<div class=relation-item onclick=jumpTo('${r.node.id}')><div class=relation-name>${r.node.label}</div><div class=relation-type>${r.rel}</div></div>`).join('')}</div>`:'<div class=detail-value>暂无关联</div>'}</div><div class=detail-section><a href=${n.url} target=_blank class=detail-url>🔗 查看归档原文</a></div>`;
  if(!n.summary&&SUMMARIES[n.id]){
    document.getElementById('detail-summary').textContent=SUMMARIES[n.id];
  } else if(!n.summary&&!SUMMARIES[n.id]){
    loadSummaries(function(){
      if(SUMMARIES[n.id]){
        var el=document.getElementById('detail-summary');
        if(el)el.textContent=SUMMARIES[n.id];
      }
    });
  }
  document.getElementById('detail').classList.add('open');
  hlG(n.id);
}'''

if 'function showDetail(n)' in content and old_showdetail not in content:
    # Try to find and replace the showDetail function
    print("⚠️  showDetail function signature found but content differs, using alternate approach")
    # Find the function and replace it
    start = content.find('function showDetail(n){')
    end = content.find('\n}', start) + 2
    if start != -1:
        content = content[:start] + new_showdetail + content[end:]
        print("✅ Replaced showDetail (alternate match)")
elif old_showdetail in content:
    content = content.replace(old_showdetail, new_showdetail)
    print("✅ Replaced showDetail")
else:
    print("⚠️  showDetail not replaced — will need manual check")

# ========== 6. 修改 renderList — summary 懒加载 ==========
old_renderlist_summary = '`<div class=card-summary>${hl(n.summary,sq)}</div>'
new_renderlist_summary = '`<div class=card-summary>${hl(n.summary||SUMMARIES[n.id]||\"\",sq)}</div>'
if old_renderlist_summary in content:
    content = content.replace(old_renderlist_summary, new_renderlist_summary)
    print("✅ Fixed renderList summary")
else:
    print("⚠️  renderList summary pattern not found")

# ========== 7. 删除底部的 KNOWLEDGE_DATA 硬编码（用 data.js 动态加载） ==========
# 在 </body> 前插入动态加载 data.js 的 script
# 先删除旧的硬编码 KNOWLEDGE_DATA
kd_start = content.find('\n<script>\nconst KNOWLEDGE_DATA')
kd_end = content.rfind('\n</script>')  # last script tag before </body>
if kd_start != -1 and kd_end != -1:
    # Also remove the closing </script> of the embedded KNOWLEDGE_DATA
    content = content[:kd_start] + content[kd_end:]
    print("✅ Removed embedded KNOWLEDGE_DATA")

# 在 </body> 前添加动态加载 data.js
body_close = content.rfind('</body>')
if body_close != -1:
    load_data_js = """
<script>
(function(){
  var xhr=new XMLHttpRequest();
  xhr.open('GET','data.js?t='+Date.now(),true);
  xhr.onload=function(){
    if(xhr.status===200){
      eval(xhr.responseText);
      if(typeof KNOWLEDGE_DATA!=='undefined'){
        D=KNOWLEDGE_DATA;
        if(typeof CATEGORY_CONFIG!=='undefined'){
          Object.keys(CATEGORY_CONFIG).forEach(function(k){CC[k]=CATEGORY_CONFIG[k];});
        }
        init();
      }
    }
  };
  xhr.onerror=function(){init();};
  xhr.send();
})();
</script>
"""
    content = content[:body_close] + load_data_js + '\n' + content[body_close:]
    print("✅ Added dynamic data.js loader")

with open(INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(content)

print("\nDone! Run: cd code-space/knowledge-graph && python3 sync-generator.py")
