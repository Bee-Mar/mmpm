import { BrowserModule } from "@angular/platform-browser";
import { NgModule, CUSTOM_ELEMENTS_SCHEMA } from "@angular/core";
import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from "./app.component";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { MaterialModule } from "./modules/material/material.module";
import { MagicMirrorModulesTableComponent } from "./components/magic-mirror-modules-table/magic-mirror-modules-table.component";
import { HttpClientModule } from "@angular/common/http";
import { ExternalSourceRegistrationDialogComponent } from "./components/external-source-registration-dialog/external-source-registration-dialog.component";
import { ReactiveFormsModule, FormsModule } from "@angular/forms";
import { MonacoEditorModule } from "ngx-monaco-editor";
import { MagicMirrorConfigEditorComponent } from "./components/magic-mirror-config-editor/magic-mirror-config-editor.component";
import { LiveTerminalFeedDialogComponent } from "src/app/components/live-terminal-feed-dialog/live-terminal-feed-dialog.component";
import { RestApiService } from "src/app/services/rest-api.service";
import { SafePipe } from "./pipes/safe.pipe";
import { TableUpdateNotifierService } from "src/app/services/table-update-notifier.service";
import { MagicMirrorControlCenterComponent } from './components/magic-mirror-control-center/magic-mirror-control-center.component';
import { ConfirmationDialogComponent } from './components/confirmation-dialog/confirmation-dialog.component';

@NgModule({
  declarations: [
    AppComponent,
    MagicMirrorModulesTableComponent,
    ExternalSourceRegistrationDialogComponent,
    MagicMirrorConfigEditorComponent,
    LiveTerminalFeedDialogComponent,
    SafePipe,
    MagicMirrorControlCenterComponent,
    ConfirmationDialogComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    MaterialModule,
    HttpClientModule,
    ReactiveFormsModule,
    FormsModule,
    MonacoEditorModule.forRoot({
      baseUrl: "./static/assets",
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
  providers: [RestApiService, TableUpdateNotifierService],
  bootstrap: [AppComponent],
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class AppModule {}
