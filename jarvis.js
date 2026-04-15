function listen(){
output.innerText="Listening...";
document.querySelector(".waveform").style.display="flex";

const r=new webkitSpeechRecognition();
r.lang=localStorage.getItem("lang")==="hi"?"hi-IN":
       localStorage.getItem("lang")==="mr"?"mr-IN":"en-IN";

r.onresult=e=>{
let cmd=e.results[0][0].transcript;
output.innerText=cmd;
speechSynthesis.speak(new SpeechSynthesisUtterance("Command received"));
};

r.onend=()=>document.querySelector(".waveform").style.display="none";
r.start();
}
