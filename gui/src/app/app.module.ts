import { BrowserModule } from "@angular/platform-browser";
import { NgModule, CUSTOM_ELEMENTS_SCHEMA, APP_INITIALIZER } from "@angular/core";
import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from "./app.component";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { MaterialModule } from "./modules/material/material.module";
import { HttpClientModule } from "@angular/common/http";
import { ExternalPackageRegistrationDialogComponent } from "./components/external-package-registration-dialog/external-package-registration-dialog.component";
import { ReactiveFormsModule, FormsModule } from "@angular/forms";
import { MonacoEditorModule } from "@materia-ui/ngx-monaco-editor";
import { MagicMirrorConfigEditorComponent } from "./components/magic-mirror-config-editor/magic-mirror-config-editor.component";
import { RestApiService } from "src/app/services/rest-api.service";
import { DataStoreService } from "src/app/services/data-store.service";
import { SafePipe } from "./pipes/safe.pipe";
import { MagicMirrorControlCenterComponent } from "./components/magic-mirror-control-center/magic-mirror-control-center.component";
import { ConfirmationDialogComponent } from "./components/confirmation-dialog/confirmation-dialog.component";
import { TerminalStyledPopUpWindowComponent } from "./components/terminal-styled-pop-up-window/terminal-styled-pop-up-window.component";
import { PackageDetailsModalComponent } from "./components/package-details-modal/package-details-modal.component";
import { ActiveProcessCountService } from "src/app/services/active-process-count.service";
import { CustomSnackbarComponent } from "./components/custom-snackbar/custom-snackbar.component";
import { MMPMMarketplaceComponent } from "./components/mmpm-marketplace/mmpm-marketplace.component";
import { MMPMLocalPackagesComponent } from "./components/mmpm-local-packages/mmpm-local-packages.component";
import { MMPMExternalPackagesComponent } from "./components/mmpm-external-packages/mmpm-external-packages.component";
import { MMPMUtility } from "src/app/utils/mmpm-utility";
import { ActiveProcessCountTickerComponent } from "./components/active-process-count-ticker/active-process-count-ticker.component";
import { ActiveProcessesModalComponent } from "./components/active-processes-modal/active-processes-modal.component";
import { InstallationConflictResolutionDialogComponent } from "./components/installation-conflict-resolution-dialog/installation-conflict-resolution-dialog.component";
import { AvailableUpgradesTickerComponent } from "./components/available-upgrades-ticker/available-upgrades-ticker.component";
import { AvailableUpgradesModalDialogComponent } from "./components/available-upgrades-modal-dialog/available-upgrades-modal-dialog.component";
import { SelectModalComponent } from "./components/select-modal/select-modal.component";
import { StoreModule } from '@ngrx/store';

export function initializeMagicMirrorPacakageData(dataStore: DataStoreService) {
  return () => dataStore.retrieveMagicMirrorPackageData();
}

@NgModule({
  declarations: [
    AppComponent,
    ExternalPackageRegistrationDialogComponent,
    MagicMirrorConfigEditorComponent,
    SafePipe,
    MagicMirrorControlCenterComponent,
    ConfirmationDialogComponent,
    TerminalStyledPopUpWindowComponent,
    PackageDetailsModalComponent,
    CustomSnackbarComponent,
    MMPMMarketplaceComponent,
    MMPMLocalPackagesComponent,
    MMPMExternalPackagesComponent,
    ActiveProcessCountTickerComponent,
    ActiveProcessesModalComponent,
    InstallationConflictResolutionDialogComponent,
    AvailableUpgradesTickerComponent,
    AvailableUpgradesModalDialogComponent,
    SelectModalComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    MaterialModule,
    HttpClientModule,
    ReactiveFormsModule,
    FormsModule,
    MonacoEditorModule,
    StoreModule.forRoot({}, {}),
  ],
  providers: [
    RestApiService,
    ActiveProcessCountService,
    MMPMUtility,
    {
      provide: APP_INITIALIZER,
      useFactory: initializeMagicMirrorPacakageData,
      deps: [DataStoreService],
      multi: true,
    },
  ],
  bootstrap: [AppComponent],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
})
export class AppModule {}
