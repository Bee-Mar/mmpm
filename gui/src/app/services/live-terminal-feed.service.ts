import { Injectable } from "@angular/core";
import io from 'socket.io-client';

@Injectable({
  providedIn: "root"
})
export class LiveTerminalFeedService {
  socket = io('http://localhost');
  constructor() {}

  ngOnInit() {
    this.socket.on('connect', (message: any) => {console.log(message)});
  }

  public getOutput() {
    // return this.socket.fromEvent<any>("message").map((data) => data.msg);
  }
}
