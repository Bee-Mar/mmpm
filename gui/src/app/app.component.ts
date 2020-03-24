import { Component } from "@angular/core";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.scss"],
  providers: []
})
export class AppComponent {
  webSSHLocation = `http://${window.location.hostname}:7892`;
  title = "gui";
}
