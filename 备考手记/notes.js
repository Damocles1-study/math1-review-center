// 备考手记：渲染公式、汇总页按科筛选、打印时展开自测答案
(function(){
  function renderMath(root){
    if(!window.katex)return;
    var w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,null),a=[],n;
    while(n=w.nextNode()){if(n.nodeValue.indexOf('$')>=0&&!n.parentNode.closest('pre,code,svg'))a.push(n);}
    a.forEach(function(t){
      var s=t.nodeValue,re=/\$\$([\s\S]+?)\$\$|\$([^$]+?)\$/g,m,last=0,f=document.createDocumentFragment();
      while(m=re.exec(s)){
        f.appendChild(document.createTextNode(s.slice(last,m.index)));
        var e=document.createElement('span');
        try{katex.render(m[1]||m[2],e,{displayMode:!!m[1],throwOnError:false,strict:false});}catch(x){e.textContent=m[0];}
        f.appendChild(e);last=m.index+m[0].length;
      }
      f.appendChild(document.createTextNode(s.slice(last)));
      t.parentNode.replaceChild(f,t);
    });
  }
  document.querySelectorAll('.sheet.m').forEach(renderMath);
  var ft=document.getElementById('ft');
  if(ft){
    ft.addEventListener('click',function(e){
      var f=e.target.getAttribute&&e.target.getAttribute('data-f');if(!f)return;
      ft.querySelectorAll('button').forEach(function(b){b.classList.toggle('on',b===e.target);});
      document.querySelectorAll('.sheet').forEach(function(s){
        var k=s.getAttribute('data-sub');
        s.classList.toggle('hide',f!=='all'&&k!==f);
      });
    });
  }
  window.addEventListener('beforeprint',function(){document.querySelectorAll('details').forEach(function(d){d.open=true;});});
})();
