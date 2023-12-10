import { APP_INITIALIZER, NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { HttpClientModule } from "@angular/common/http";
import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from "./app.component";
import { MmpmMarketPlaceComponent } from "@/magicmirror/components/mmpm-marketplace/mmpm-marketplace.component";
import { SharedStoreService } from "@/services/shared-store.service";
import { LogStreamViewerComponent } from "./components/log-stream-viewer/log-stream-viewer.component";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { MonacoEditorModule } from "ngx-monaco-editor-v2";
import { ConfigEditorComponent } from "./components/config-editor/config-editor.component";
import { PrimeNgModule } from "./modules/primeng.module";
import { DatabaseInfoComponent } from "./components/database-info/database-info.component";
import { CustomPackageManagerComponent } from "./components/custom-package-manager/custom-package-manager.component";

export function init_shared_store(store: SharedStoreService) {
  return () => store.getPackages();
}

@NgModule({
  declarations: [AppComponent, MmpmMarketPlaceComponent, LogStreamViewerComponent, ConfigEditorComponent, DatabaseInfoComponent, CustomPackageManagerComponent],
  imports: [BrowserAnimationsModule, BrowserModule, AppRoutingModule, HttpClientModule, PrimeNgModule, MonacoEditorModule.forRoot()],
  providers: [
    {
      provide: APP_INITIALIZER,
      useFactory: init_shared_store,
      deps: [SharedStoreService],
      multi: true,
    },
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
