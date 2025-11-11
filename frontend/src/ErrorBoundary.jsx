import React from "react";
export default class ErrorBoundary extends React.Component {
  constructor(p){ super(p); this.state={hasError:false,err:null}; }
  static getDerivedStateFromError(err){ return {hasError:true,err}; }
  componentDidCatch(err,info){ console.error("[ErrorBoundary]", err, info); }
  render(){
    if(this.state.hasError){
      return <div style={{padding:16,fontFamily:"system-ui",color:"#111",background:"#fff"}}>
        <h2>Une erreur est survenue.</h2>
        <pre style={{whiteSpace:"pre-wrap"}}>{String(this.state.err||"")}</pre>
      </div>;
    }
    return this.props.children;
  }
}
