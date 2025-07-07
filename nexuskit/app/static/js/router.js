class Router {
  constructor(routes) {
    this.routes = routes;
    this.appContainer = document.getElementById("app-container");
    window.addEventListener("hashchange", this.handleRouteChange.bind(this));
    this.handleRouteChange(); // Handle initial route
  }

  handleRouteChange() {
    const path = window.location.hash.slice(1) || "/";
    const route = this.routes[path];
    if (route) {
      this.loadView(route);
    } else {
      this.appContainer.innerHTML = "<h2>404 - Not Found</h2>";
    }
  }

  async loadView(view) {
    try {
      const response = await fetch(`/static/views/${view.template}`);
      const html = await response.text();
      this.appContainer.innerHTML = html;

      if (view.script) {
        // Remove old script if it exists
        const oldScript = document.getElementById("tool-script");
        if (oldScript) {
          oldScript.remove();
        }

        // Add new script
        const script = document.createElement("script");
        script.id = "tool-script";
        script.src = `/static/js/${view.script}?v=${new Date().getTime()}`;
        script.onload = () => {
          if (typeof view.init === "function") {
            view.init();
          }
        };
        document.body.appendChild(script);
      }
    } catch (error) {
      console.error("Error loading view:", error);
      this.appContainer.innerHTML = "<h2>Error loading page</h2>";
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const routes = {
    "/": { template: "dashboard.html" },
    "/ytdl": { template: "ytdl.html", script: "ytdl.js", init: ytdl },
    "/pdf-editor": {
      template: "pdf_editor.html",
      script: "pdf_editor.js",
      init: pdfEditor,
    },
    "/ffmpeg-converter": {
      template: "ffmpeg_converter.html",
      script: "ffmpeg_converter.js",
      init: ffmpegConverter,
    },
    "/image-editor": {
      template: "image_editor.html",
      script: "image_editor.js",
      init: imageEditor,
    },
    "/formatter": {
      template: "formatter.html",
      script: "formatter.js",
      init: formatter,
    },
  };
  new Router(routes);
});
