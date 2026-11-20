
  (() => {
    const root = document.getElementById('queen-parts-map');
    const svg = root.querySelector('svg');
    const image = root.querySelector('.queen-photo');
    const callouts = root.querySelector('.part-callouts');
    const focus = root.querySelector('.part-focus-layer');
    const buttons = [...root.querySelectorAll('[data-part]')];
    const ns = 'http://www.w3.org/2000/svg';
    const parts = [
      {id:1,name:'Finial',description:'The egg-shaped center emerging from the bowl.',point:[483,205],badge:[680,203],elbow:[587,203],region:[483,218,55,60]},
      {id:2,name:'Crown tips',description:'The eight raised points around the crown.',point:[550,67],badge:[680,80],elbow:[588,80],region:[550,78,20,30]},
      {id:3,name:'Crown rim',description:'The thick, rounded lip running between the tips.',point:[568,329],badge:[690,345],elbow:[620,345],region:[562,329,43,20]},
      {id:4,name:'Inner bowl',description:'The shallow scooped surface surrounding the finial.',point:[399,268],badge:[248,225],elbow:[320,225],region:[399,265,35,29]},
      {id:5,name:'Crown body',description:'The upper neck: the short body below the crown and above the collars.',point:[455,393],badge:[255,390],elbow:[350,390],region:[480,392,96,38]},
      {id:6,name:'Upper collar',description:'The smallest rounded ring, directly beneath the crown body.',point:[483,452],badge:[685,460],elbow:[600,460],region:[483,452,57,10]},
      {id:7,name:'Middle collar',description:'The middle projecting ring in the three-ring stack.',point:[483,509],badge:[247,535],elbow:[340,535],region:[483,509,58,10]},
      {id:8,name:'Lower collar',description:'The widest, lowest ring of the collar stack, above the stem.',point:[483,551],badge:[690,585],elbow:[620,585],region:[483,550,55,10]},
      {id:9,name:'Stem',description:'The long, tapered shaft between the collar stack and the base.',point:[480,633],badge:[257,630],elbow:[360,630],region:[483,646,67,65]},
      {id:10,name:'Stem seat',description:'The narrow junction where the bottom of the stem enters its raised support.',point:[473,749],badge:[687,743],elbow:[590,743],region:[473,746,58,9]},
      {id:11,name:'Raised socket',description:'The rounded supporting ring and short wall beneath the stem seat.',point:[465,793],badge:[247,828],elbow:[337,828],region:[483,793,76,26]},
      {id:12,name:'Flared base',description:'The broad, sloping main body of the base.',point:[520,909],badge:[706,945],elbow:[628,945],region:[499,901,90,61]},
      {id:13,name:'Base groove',description:'The single recessed lathe line separating the flared base from the foot.',point:[463,1025],badge:[253,1030],elbow:[350,1030],region:[471,1024,66,9]},
      {id:14,name:'Foot',description:'The lowest rounded band that the piece stands on.',point:[485,1064],badge:[690,1070],elbow:[606,1070],region:[485,1061,63,13]}
    ];
    let selected = 9;
    const valid = value => parts.some(part => part.id === Number(value));
    const saved = window.openai?.widgetState;
    if (valid(saved?.privateContent?.selectedPart)) selected = Number(saved.privateContent.selectedPart);
    else if (valid(saved?.modelContent?.partNumber)) selected = Number(saved.modelContent.partNumber);
    function element(tag,attributes,text) {
      const node = document.createElementNS(ns,tag);
      Object.entries(attributes).forEach(([key,value]) => node.setAttribute(key,String(value)));
      if (text !== undefined) node.textContent = text;
      return node;
    }
    function draw() {
      const width = root.querySelector('.parts-picture').clientWidth;
      if (!width) return;
      const scale = width / 610, height = 1075 * scale;
      const xy = ([x,y]) => [(x-180)*scale,(y-35)*scale];
      svg.setAttribute('viewBox',`0 0 ${width} ${height}`);
      svg.style.height = height+'px';
      image.setAttribute('width',width);image.setAttribute('height',height);
      callouts.replaceChildren();focus.replaceChildren();
      parts.forEach(part => {
        const group = element('g',{class:part.id===selected?'active':''});
        const p=xy(part.point),b=xy(part.badge),e=xy(part.elbow);
        group.append(element('path',{class:'part-line',d:`M${b[0]} ${b[1]} L${e[0]} ${e[1]} L${p[0]} ${p[1]}`}));
        group.append(element('circle',{class:'part-dot',cx:p[0],cy:p[1],r:2.5}));
        group.append(element('circle',{class:'part-badge',cx:b[0],cy:b[1],r:12}));
        group.append(element('text',{class:'part-number',x:b[0],y:b[1]},part.id));
        callouts.append(group);
        if(part.id===selected) {
          const [x,y,rx,ry]=part.region,c=xy([x,y]);
          focus.append(element('ellipse',{class:'part-focus',cx:c[0],cy:c[1],rx:rx*scale,ry:ry*scale}));
        }
      });
    }
    function select(id,persist=false) {
      if(!valid(id)) return;
      selected=Number(id);
      const part=parts.find(part=>part.id===selected);
      buttons.forEach(button=>button.setAttribute('aria-pressed',String(Number(button.dataset.part)===selected)));
      root.querySelector('.part-selected-name').textContent=`${part.id} · ${part.name}`;
      root.querySelector('.part-selected-description').textContent=' — '+part.description;
      draw();
      if(persist&&window.openai?.setWidgetState) {
        window.openai.setWidgetState({modelContent:{partNumber:part.id,partName:part.name},privateContent:{selectedPart:part.id}}).catch(()=>{});
      }
    }
    buttons.forEach(button=>button.addEventListener('click',()=>select(button.dataset.part,true)));
    window.addEventListener('openai:set_globals',event=>{
      const state=event.detail?.globals?.widgetState;
      const id=state?.privateContent?.selectedPart??state?.modelContent?.partNumber;
      if(valid(id)) select(id);
    });
    new ResizeObserver(draw).observe(root.querySelector('.parts-picture'));
    select(selected);
  })();
  