import { APP_INITIALIZER, NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { HttpClientModule } from "@angular/common/http";
import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from "./app.component";
import { MmpmMarketPlaceComponent } from "@/magicmirror/components/mmpm-marketplace/mmpm-marketplace.component";
import { SharedStoreService } from "@/services/shared-store.service";
import { TableModule } from "primeng/table";

import { BrowserAnimationsModule } from "@angular/platform-browser/animations";

export function init_shared_store(store: SharedStoreService) {
  return () => store.get_packages();
}

@NgModule({
  declarations: [AppComponent, MmpmMarketPlaceComponent],
  imports: [BrowserAnimationsModule, BrowserModule, AppRoutingModule, HttpClientModule, TableModule],
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
