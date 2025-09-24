import { Injectable, NgZone } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ChatService {
  private apiUrl = 'http://127.0.0.1:8000/api/chat/'; // adapte à ton backend

  constructor(private zone: NgZone) {}

  sendMessage(message: string): Observable<any> {
    return new Observable((observer) => {
      fetch(this.apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      })
        .then((response) => {
          if (!response.body) throw new Error('Pas de flux SSE depuis le serveur');
          const reader = response.body.getReader();
          const decoder = new TextDecoder('utf-8');

          const read = () => {
            reader.read().then(({ done, value }) => {
              if (done) {
                observer.complete();
                return;
              }
              const chunk = decoder.decode(value, { stream: true });
              // découpe en events SSE simples
              chunk.split('\n\n').forEach((event) => {
                const line = event.trim();
                if (!line) return;
                if (line.startsWith('event:')) {
                  const [, rest] = line.split('event:');
                  const evt = rest.trim().split('\n')[0];
                  // find data line
                  const dataLine = event.split('\n').find(l => l.trim().startsWith('data:'));
                  if (!dataLine) return;
                  const raw = dataLine.replace(/^data:\s*/, '').trim();
                  try {
                    const parsed = JSON.parse(raw);
                    if (evt === 'token') this.zone.run(() => observer.next({ type: 'token', data: parsed }));
                    else if (evt === 'full') this.zone.run(() => observer.next({ type: 'full', data: parsed }));
                    else if (evt === 'sources') this.zone.run(() => observer.next({ type: 'sources', data: parsed }));
                  } catch (e) {
                    // fallback: plain text
                    this.zone.run(() => observer.next({ type: 'token', data: { text: raw } }));
                  }
                } else {
                  // maybe raw text
                  this.zone.run(() => observer.next({ type: 'token', data: { text: event } }));
                }
              });
              read();
            });
          };
          read();
        })
        .catch((err) => observer.error(err));
    });
  }
}
