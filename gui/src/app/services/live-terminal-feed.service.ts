import { Injectable } from "@angular/core";
import io from "socket.io-client";
import { Observable } from "rxjs";

@Injectable({
  providedIn: "root"
})
export class LiveTerminalFeedService {
  socket: any;
  observable: Observable<object>;

  constructor() {
  }

  public getSocket() {
    return io("http://127.0.0.1:7891", {
      reconnection: true,
      transports: ["websocket", "polling"]
    });
  }
}
