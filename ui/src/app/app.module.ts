import { APP_INITIALIZER, NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { HttpClientModule } from "@angular/common/http";
import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from "./app.component";
import { MarketPlaceComponent } from "@/components/marketplace/marketplace.component";
import { SharedStoreService } from "@/services/shared-store.service";
import { LogStreamViewerComponent } from "./components/log-stream-viewer/log-stream-viewer.component";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { MonacoEditorModule } from "ngx-monaco-editor-v2";
import { ConfigEditorComponent } from "./components/config-editor/config-editor.component";
import { PrimeNgModule } from "./modules/primeng.module";
import { DatabaseInfoComponent } from "./components/database-info/database-info.component";
import { CustomPackageManagerComponent } from "./components/custom-package-manager/custom-package-manager.component";
import { PackageDetailsViewerComponent } from "./components/package-details-viewer/package-details-viewer.component";
import { ShoppingCartComponent } from "./components/shopping-cart/shopping-cart.component";
import { MagicMirrorControllerComponent } from "./components/magicmirror-controller/magicmirror-controller.component";
import { MirrorPreviewComponent } from "./components/mirror-preview/mirror-preview.component";
import { CurrentlyInstalledComponent } from "./components/currently-installed/currently-installed.component";
import { providePrimeNG } from "primeng/config";
import Aura from "@primeuix/themes/aura";

export function init_shared_store(store: SharedStoreService) {
  return () => store.load();
}

@NgModule({
  declarations: [
    AppComponent,
    MarketPlaceComponent,
    LogStreamViewerComponent,
    ConfigEditorComponent,
    DatabaseInfoComponent,
    CustomPackageManagerComponent,
    PackageDetailsViewerComponent,
    ShoppingCartComponent,
    MagicMirrorControllerComponent,
    MirrorPreviewComponent,
    CurrentlyInstalledComponent,
  ],
  imports: [BrowserAnimationsModule, BrowserModule, AppRoutingModule, HttpClientModule, PrimeNgModule, MonacoEditorModule.forRoot()],
  providers: [
    {
      provide: APP_INITIALIZER,
      useFactory: init_shared_store,
      deps: [SharedStoreService],
      multi: true,
    },
    providePrimeNG({
      theme: {
        preset: Aura,
        options: {
          darkModeSelector: false,
        },
      },
    }),
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
