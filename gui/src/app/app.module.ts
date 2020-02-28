import { BrowserModule } from "@angular/platform-browser";
import { NgModule } from "@angular/core";
import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from "./app.component";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { MaterialModule } from "./modules/material/material.module";
import { MagicMirrorModulesTableComponent } from "./components/magic-mirror-modules-table/magic-mirror-modules-table.component";
import { HttpClientModule } from "@angular/common/http";
import { EmbeddedTerminalComponent } from "./components/embedded-terminal/embedded-terminal.component";
import { NgTerminalModule } from "ng-terminal";
import { ExternalSourceRegistrationFormComponent } from "./components/external-source-registration-form/external-source-registration-form.component";
import { ReactiveFormsModule, FormsModule } from "@angular/forms";
import { MonacoEditorModule } from "ngx-monaco-editor";
import { MagicMirrorConfigEditorComponent } from "./components/magic-mirror-config-editor/magic-mirror-config-editor.component";

@NgModule({
  declarations: [
    AppComponent,
    MagicMirrorModulesTableComponent,
    EmbeddedTerminalComponent,
    ExternalSourceRegistrationFormComponent,
    MagicMirrorConfigEditorComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    MaterialModule,
    HttpClientModule,
    NgTerminalModule,
    ReactiveFormsModule,
    FormsModule,
    MonacoEditorModule.forRoot({
      baseUrl: "assets", // configure base path for monaco editor default: './assets'
      defaultOptions: {
        language: "javascript",
        scrollBeyondLastLine: false,
        minimap: {
          enabled: false
        },
        scrollbar: {
          useShadows: true,
          verticalHasArrows: false,
          horizontalHasArrows: false,
          vertical: "visible",
          verticalScrollbarSize: 12,
          horizontalScrollbarSize: 12,
          arrowSize: 30
        },
        automaticLayout: true
      }
    })
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {}
