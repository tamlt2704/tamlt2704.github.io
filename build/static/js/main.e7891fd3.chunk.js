(this.webpackJsonplesgent=this.webpackJsonplesgent||[]).push([[0],{19:function(e,t,a){e.exports=a.p+"static/media/cybereye.466fa6a0.jpg"},24:function(e,t,a){},34:function(e,t,a){e.exports=a.p+"static/media/face-recognition.34bd6591.jpg"},37:function(e,t,a){e.exports=a(59)},43:function(e,t,a){},44:function(e,t,a){e.exports=a.p+"static/media/logo.5d5d9eef.svg"},45:function(e,t,a){},52:function(e,t){},53:function(e,t){},54:function(e,t){},59:function(e,t,a){"use strict";a.r(t);a(38);var n=a(1),r=a.n(n),o=a(33),i=a.n(o),c=(a(43),a(44),a(24),a(7)),s=a(19),l=a.n(s);function u(e){return Object(c.a)(e),r.a.createElement(r.a.Fragment,null,r.a.createElement("nav",{className:"navbar navbar-expand-lg navbar-light navbar-dark",style:{backgroundColor:"#425b76"}},r.a.createElement("img",{src:l.a,alt:"",style:{width:40,height:40,borderRadius:50}})," \xa0",r.a.createElement("a",{className:"navbar-brand",href:"/"},"cyber eye"),r.a.createElement("button",{className:"navbar-toggler",type:"button","data-toggle":"collapse","data-target":"#navbarNav","aria-controls":"navbarNav","aria-expanded":"false","aria-label":"Toggle navigation"},r.a.createElement("span",{className:"navbar-toggler-icon"})),r.a.createElement("div",{className:"collapse navbar-collapse",id:"navbarNav"},r.a.createElement("ul",{className:"navbar-nav"},r.a.createElement("li",{className:"nav-item active"},r.a.createElement("a",{className:"nav-link",href:"/"},"Home ",r.a.createElement("span",{className:"sr-only"},"(current)"))),r.a.createElement("li",{className:"nav-item"},r.a.createElement("a",{className:"nav-link",href:"/products"},"Products")),r.a.createElement("li",{className:"nav-item"},r.a.createElement("a",{className:"nav-link",href:"/about"},"About Us")),r.a.createElement("li",{className:"nav-item"},r.a.createElement("a",{className:"nav-link",href:"#"},"Get in touch"))))))}u.defaultProps={};var m=u;function d(e){return Object(c.a)(e),r.a.createElement(r.a.Fragment,null,r.a.createElement("div",{style:{clear:"both"}}),r.a.createElement("div",{className:"row navbar fixed-bottom",style:{backgroundColor:"#f4f4f4"}},r.a.createElement("div",{className:"col"},r.a.createElement("div",null,r.a.createElement("img",{src:l.a,alt:"",style:{width:40,height:40,borderRadius:50}})," \xa0 Cyber Eye")),r.a.createElement("div",{className:"col"},r.a.createElement("p",null,"Products"),r.a.createElement("p",null,"Face Recognition")),r.a.createElement("div",{className:"col"},r.a.createElement("p",null,r.a.createElement("a",{href:"/about"},"About Us")),r.a.createElement("p",null,r.a.createElement("a",{href:"/about/news"},"News")),r.a.createElement("p",null,r.a.createElement("a",{href:"/about/demos"},"Demos")))))}d.defaultProps={};var h=a(25),v=a(36),f=a(9);function p(e){Object(c.a)(e);var t,a=Object(n.useRef)(),o=Object(n.useState)({width:window.innerWidth,height:600}),i=Object(f.a)(o,2),s=i[0],l=i[1],u=(t=20,Object(v.a)(Array(t))).map((function(e,t){var a=Math.random()*s.width,n=Math.random()*s.height,r=3*Math.random();return{x:a,y:n,radius:r,originRadius:r}})),m=Object(n.useState)(u),d=Object(f.a)(m,2),p=d[0],g=(d[1],Object(n.useState)(null)),b=Object(f.a)(g,2),E=b[0],w=b[1],y=0,k=function e(t){if(t-y>150){var n=a.current,r=n.getContext("2d"),o=n.width,i=n.height;r.strokeStyle="balck",r.fillStyle="#425b76",r.fillRect(0,0,o,i),r.fillStyle="white";var c,l=Object(h.a)(p);try{for(l.s();!(c=l.n()).done;){var u=c.value;u.x+=Math.random()*(Math.floor(2*Math.random())?1:-1),u.x%=s.width,u.y+=Math.random(),u.y%=s.height;var m=u.x,d=u.y,v=u.radius;r.beginPath(),r.arc(m,d,v,0,2*Math.PI,!1),r.fill()}}catch(f){l.e(f)}finally{l.f()}y=t}w(requestAnimationFrame(e))};return Object(n.useEffect)((function(){return console.log("use effect"),w(requestAnimationFrame(k)),function(){console.log("cancel raf"),cancelAnimationFrame(E)}}),[p]),Object(n.useEffect)((function(){function e(){console.log("onReize"),l({width:window.innerWidth,height:600})}return function(){window.removeEventListener("resize",e)}})),r.a.createElement("div",{className:"row"},r.a.createElement("canvas",{ref:a,width:s.width,height:s.height,onMouseMove:function(e){var t,n=e.clientX,r=e.clientY,o=[],i=Object(h.a)(p);try{for(i.s();!(t=i.n()).done;){var c=t.value,s=c.x,l=c.y,u=n-s,m=r-l,d=Math.sqrt(u*u+m*m);c.radius=d<100?3:c.originRadius,d<100&&o.push(c)}}catch(w){i.e(w)}finally{i.f()}for(var v=a.current.getContext("2d"),f=0;f<o.length;f++){var g=Math.floor(Math.random()*o.length),b=o[f],E=o[g];v.beginPath(),v.moveTo(b.x,b.y),v.lineTo(E.x,E.y),v.stroke()}}}))}p.defaultProps={};var g=p,b=a(34),E=a.n(b);function w(e){return Object(c.a)(e),r.a.createElement("div",{className:"row"},r.a.createElement("div",{className:"card",style:{width:"18rem"}},r.a.createElement("img",{className:"card-img-top",src:E.a,alt:"Card image cap"}),r.a.createElement("div",{className:"card-body"},r.a.createElement("h5",{className:"card-title"},"Card title"),r.a.createElement("p",{className:"card-text"},"Some quick example text to build on the card title and make up the bulk of the card's content."),r.a.createElement("a",{href:"#",className:"btn btn-primary"},"Go somewhere"))))}w.defaultProps={};var y=w;function k(e){return Object(c.a)(e),r.a.createElement("div",{className:"row"},"App Demo 02")}k.defaultProps={};var x=k;function P(){return r.a.createElement(r.a.Fragment,null,r.a.createElement(g,null," "),r.a.createElement(y,null),r.a.createElement(x,null))}function j(){return r.a.createElement("div",null,r.a.createElement("h1",null,"[About]"))}function O(){return r.a.createElement("div",null,r.a.createElement("h1",null,"[Products]"))}function N(){return r.a.createElement("div",null,r.a.createElement("h1",null,"[News]"))}function C(){return r.a.createElement(r.a.Fragment,null)}function S(){return r.a.createElement("div",null,r.a.createElement("h1",null,"[Whoop404]"))}var M=a(2);a(45);function F(e){return Object(c.a)(e),r.a.createElement(r.a.Fragment,null)}F.defaultProps={},F.propTypes={};var D=F,W=a(4),R=a.n(W),T=a(10),H=a(20),A=a(17),I=a(22),V=a(21),U=a(11);function q(e){return[e.x,e.y]}function z(e,t,a,n){var r=arguments.length>4&&void 0!==arguments[4]?arguments[4]:1;e.forEach((function(e){if(e.score>=t){var o=e.position,i=o.x,c=o.y;n.beginPath(),n.arc(i*r,c*r,3,0,2*Math.PI),n.fillStyle=a,n.fill()}}))}function L(e,t,a,n,r,o){var i=Object(f.a)(e,2),c=i[0],s=i[1],l=Object(f.a)(t,2),u=l[0],m=l[1];o.beginPath(),o.moveTo(c*r,s*r),o.lineTo(u*r,m*r),o.lineWidth=n,o.strokeStyle=a,o.stroke()}function B(e,t,a,n,r){var o=arguments.length>5&&void 0!==arguments[5]?arguments[5]:1;U.a(e,t);L(q(e[0].position),q(e[1].position),a,n,o,r)}var G=function(e){Object(I.a)(a,e);var t=Object(V.a)(a);function a(e){var n;return Object(H.a)(this,a),(n=t.call(this,e,a.defaultProps)).getCanvas=function(e){n.canvas=e},n.getVideo=function(e){n.video=e},n}return Object(A.a)(a,[{key:"setupCamera",value:function(){var e=Object(T.a)(R.a.mark((function e(){var t,a,n,r,o;return R.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:if(!(!navigator.mediaDevices|!navigator.mediaDevices.getUserMedia)){e.next=2;break}throw new Error("Browser API navigator.mediaDevices.getUserMedia not available");case 2:return console.log(this.props),t=this.props,a=t.videoWidth,n=t.videoHeight,(r=this.video).width=a,r.height=n,e.next=9,navigator.mediaDevices.getUserMedia({audio:!1,video:{facingMode:"user",width:a,height:n}});case 9:return o=e.sent,r.srcObject=o,e.abrupt("return",new Promise((function(e){r.onloadedmetadata=function(){e(r)}})));case 12:case"end":return e.stop()}}),e,this)})));return function(){return e.apply(this,arguments)}}()},{key:"loadVideo",value:function(){var e=Object(T.a)(R.a.mark((function e(){var t;return R.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,this.setupCamera();case 2:return(t=e.sent).play(),e.abrupt("return",t);case 5:case"end":return e.stop()}}),e,this)})));return function(){return e.apply(this,arguments)}}()},{key:"detectPose",value:function(){var e=this.props,t=e.videoWidth,a=e.videoHeight,n=this.canvas,r=n.getContext("2d");n.width=t,n.height=a,this.poseDetectionFrame(r)}},{key:"poseDetectionFrame",value:function(e){var t=this.props,a=t.algorithm,n=t.imageScaleFactor,r=t.flipHorizontal,o=t.outputStride,i=t.minPoseConfidence,c=t.minPartConfidence,s=t.maxPoseDetections,l=t.nmsRadius,u=t.videoWidth,m=t.videoHeight,d=t.showVideo,h=t.showPoints,v=t.showSkeleton,f=t.skeletonColor,p=t.skeletonLineWidth,g=this.posenet,b=this.video,E=function(){var t=Object(T.a)(R.a.mark((function t(){var w,y;return R.a.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:w=[],t.t0=a,t.next="multi-pose"===t.t0?4:"single-pose"===t.t0?8:13;break;case 4:return t.next=6,g.estimateMultiplePoses(b,n,r,o,s,c,l);case 6:return w=t.sent,t.abrupt("break",13);case 8:return t.next=10,g.estimateSinglePose(b,n,r,o);case 10:return y=t.sent,w.push(y),t.abrupt("break",13);case 13:e.clearRect(0,0,u,m),d&&(e.save(),e.scale(-1,1),e.translate(-u,0),e.drawImage(b,0,0,u,m),e.restore()),w.forEach((function(t){var a=t.score,n=t.keypoints;a>i&&(h&&z(n,c,f,e),v&&B(n,c,f,p,e))})),requestAnimationFrame(E);case 17:case"end":return t.stop()}}),t)})));return function(){return t.apply(this,arguments)}}();E()}},{key:"componentDidMount",value:function(){var e=Object(T.a)(R.a.mark((function e(){var t=this;return R.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.prev=0,e.next=3,this.setupCamera();case 3:e.next=9;break;case 5:throw e.prev=5,e.t0=e.catch(0),console.log(e.t0),new Error("This browser does not support video capture, or this video does not have a camera");case 9:return e.prev=9,e.next=12,U.b();case 12:this.posenet=e.sent,e.next=18;break;case 15:throw e.prev=15,e.t1=e.catch(9),new Error("posenet failed to load");case 18:return e.prev=18,setTimeout((function(){t.setState({loading:!1})}),200),e.finish(18);case 21:console.log("doneeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"),this.detectPose();case 23:case"end":return e.stop()}}),e,this,[[0,5],[9,15,18,21]])})));return function(){return e.apply(this,arguments)}}()}]),Object(A.a)(a,[{key:"render",value:function(){return r.a.createElement(r.a.Fragment,null,r.a.createElement("video",{id:"videoNoShow",playsInline:!0,ref:this.getVideo}),r.a.createElement("canvas",{className:"webcam",ref:this.getCanvas}))}}]),a}(r.a.Component);G.defaultProps={videoWidth:900,videoHeight:700,flipHorizontal:!0,algorithm:"single-pose",showVideo:!0,showSkeleton:!0,showPoints:!0,minPoseConfidence:.1,minPartConfidence:.5,maxPoseDetections:2,nmsRadius:20,outputStride:16,imageScaleFactor:.5,skeletonColor:"#ffadea",skeletonLineWidth:6,loadingText:"loading .... please wait ...."};function J(e){return[e.x,e.y]}function X(e,t,a,n){var r=arguments.length>4&&void 0!==arguments[4]?arguments[4]:1;e.forEach((function(e){if(e.score>=t){var o=e.position,i=o.x,c=o.y;n.beginPath(),n.arc(i*r,c*r,3,0,2*Math.PI),n.fillStyle=a,n.fill()}}))}function Y(e,t,a,n,r,o){var i=Object(f.a)(e,2),c=i[0],s=i[1],l=Object(f.a)(t,2),u=l[0],m=l[1];o.beginPath(),o.moveTo(c*r,s*r),o.lineTo(u*r,m*r),o.lineWidth=n,o.strokeStyle=a,o.stroke()}function $(e,t,a,n,r){var o=arguments.length>5&&void 0!==arguments[5]?arguments[5]:1,i=U.a(e,t);i.forEach((function(e){Y(J(e[0].position),J(e[1].position),a,n,o,r)}))}var K=function(e){Object(I.a)(a,e);var t=Object(V.a)(a);function a(e){var n;return Object(H.a)(this,a),(n=t.call(this,e,a.defaultProps)).getCanvas=function(e){n.canvas=e},n.getVideo=function(e){n.video=e},n}return Object(A.a)(a,[{key:"componentDidMount",value:function(){var e=Object(T.a)(R.a.mark((function e(){var t=this;return R.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.prev=0,e.next=3,this.setupCamera();case 3:e.next=8;break;case 5:throw e.prev=5,e.t0=e.catch(0),new Error("This browser does not support video capture, or this device does not have a camera");case 8:return e.prev=8,e.next=11,U.b();case 11:this.posenet=e.sent,e.next=17;break;case 14:throw e.prev=14,e.t1=e.catch(8),new Error("PoseNet failed to load");case 17:return e.prev=17,setTimeout((function(){t.setState({loading:!1})}),200),e.finish(17);case 20:this.detectPose();case 21:case"end":return e.stop()}}),e,this,[[0,5],[8,14,17,20]])})));return function(){return e.apply(this,arguments)}}()},{key:"setupCamera",value:function(){var e=Object(T.a)(R.a.mark((function e(){var t,a,n,r,o;return R.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:if(navigator.mediaDevices&&navigator.mediaDevices.getUserMedia){e.next=2;break}throw new Error("Browser API navigator.mediaDevices.getUserMedia not available");case 2:return t=this.props,a=t.videoWidth,n=t.videoHeight,(r=this.video).width=a,r.height=n,e.next=8,navigator.mediaDevices.getUserMedia({audio:!1,video:{facingMode:"user",width:a,height:n}});case 8:return o=e.sent,r.srcObject=o,e.abrupt("return",new Promise((function(e){r.onloadedmetadata=function(){r.play(),e(r)}})));case 11:case"end":return e.stop()}}),e,this)})));return function(){return e.apply(this,arguments)}}()},{key:"detectPose",value:function(){var e=this.props,t=e.videoWidth,a=e.videoHeight,n=this.canvas,r=n.getContext("2d");n.width=t,n.height=a,this.poseDetectionFrame(r)}},{key:"poseDetectionFrame",value:function(e){var t=this.props,a=t.algorithm,n=t.imageScaleFactor,r=t.flipHorizontal,o=t.outputStride,i=t.minPoseConfidence,c=t.minPartConfidence,s=t.maxPoseDetections,l=t.nmsRadius,u=t.videoWidth,m=t.videoHeight,d=t.showVideo,h=t.showPoints,v=t.showSkeleton,f=t.skeletonColor,p=t.skeletonLineWidth,g=this.posenet,b=this.video,E=function(){var t=Object(T.a)(R.a.mark((function t(){var w,y;return R.a.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:w=[],t.t0=a,t.next="multi-pose"===t.t0?4:"single-pose"===t.t0?8:13;break;case 4:return t.next=6,g.estimateMultiplePoses(b,n,r,o,s,c,l);case 6:return w=t.sent,t.abrupt("break",13);case 8:return t.next=10,g.estimateSinglePose(b,n,r,o);case 10:return y=t.sent,w.push(y),t.abrupt("break",13);case 13:e.clearRect(0,0,u,m),d&&(e.save(),e.scale(-1,1),e.translate(-u,0),e.drawImage(b,0,0,u,m),e.restore()),w.forEach((function(t){var a=t.score,n=t.keypoints;a>=i&&(h&&X(n,c,f,e),v&&$(n,c,f,p,e))})),requestAnimationFrame(E);case 17:case"end":return t.stop()}}),t)})));return function(){return t.apply(this,arguments)}}();E()}},{key:"render",value:function(){return r.a.createElement("div",null,r.a.createElement("div",null,r.a.createElement("video",{id:"videoNoShow",playsInline:!0,ref:this.getVideo}),r.a.createElement("canvas",{className:"webcam",ref:this.getCanvas})))}}]),a}(n.Component);K.defaultProps={videoWidth:900,videoHeight:700,flipHorizontal:!0,algorithm:"single-pose",showVideo:!0,showSkeleton:!0,showPoints:!0,minPoseConfidence:.1,minPartConfidence:.5,maxPoseDetections:2,nmsRadius:20,outputStride:16,imageScaleFactor:.5,skeletonColor:"#ffadea",skeletonLineWidth:6,loadingText:"Loading...please be patient..."};var Q=K;var Z=function(){return r.a.createElement(r.a.Fragment,null,r.a.createElement(m,null," "),r.a.createElement("div",{className:"container-fluid"},r.a.createElement(M.d,null,r.a.createElement(M.a,{from:"/demos",to:"/about/demos"}),r.a.createElement(M.a,{from:"/news",to:"/about/news"}),r.a.createElement(M.b,{exact:!0,path:"/",component:P}),r.a.createElement(M.b,{path:"/products",component:O}),r.a.createElement(M.b,{path:"/about",render:function(e){var t=e.match.url;return r.a.createElement(r.a.Fragment,null,r.a.createElement(M.b,{path:"".concat(t,"/"),component:j,exact:!0}),r.a.createElement(M.b,{path:"".concat(t,"/news"),component:N,exact:!0}),r.a.createElement(M.b,{path:"".concat(t,"/demos"),component:C,exact:!0}))}}),r.a.createElement(M.b,{exact:!0,path:"/pushup",component:Q}),r.a.createElement(M.b,{exact:!0,path:"/admin",component:D}),r.a.createElement(M.b,{path:"*",component:S}))))};Boolean("localhost"===window.location.hostname||"[::1]"===window.location.hostname||window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/));var _=a(18);i.a.render(r.a.createElement(r.a.StrictMode,null,r.a.createElement(_.a,null,r.a.createElement(Z,null))),document.getElementById("root")),"serviceWorker"in navigator&&navigator.serviceWorker.ready.then((function(e){e.unregister()})).catch((function(e){console.error(e.message)}))}},[[37,1,2]]]);
//# sourceMappingURL=main.e7891fd3.chunk.js.map