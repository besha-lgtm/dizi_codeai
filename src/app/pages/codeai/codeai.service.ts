import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, interval, switchMap, takeWhile, map } from 'rxjs';

export interface ReviewIssue {
  line: number | null;
  category: string;
  issue: string;
  recommendation: string;
}

export interface ReviewFile {
  file_name: string;
  file_path: string;
  status: 'good' | 'issues_found';
  issues: ReviewIssue[];
}

export interface ReviewResult {
  overall_status: 'good' | 'issues_found';
  summary: string;
  files: ReviewFile[];
  repository_url: string;
  audit_type: string;
  files_found: number;
  files_processed: number;
}

export interface ReviewJob {
  job_id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  result?: ReviewResult;
  error?: string;
}

@Injectable({ providedIn: 'root' })
export class CodeAiService {
  private readonly BASE = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  startReview(
    repositoryUrl: string,
    auditType: string,
    model: string
  ): Observable<{ job_id: string; status: string; message: string }> {
    return this.http.post<any>(`${this.BASE}/review`, {
      repository_url: repositoryUrl,
      audit_type: auditType.toLowerCase(),
      model: model.toLowerCase(),
    });
  }

  getStatus(jobId: string): Observable<ReviewJob> {
    return this.http.get<ReviewJob>(`${this.BASE}/review/${jobId}`);
  }

  /**
   * Polls every 3 s until job is completed or failed.
   */
  pollUntilDone(jobId: string): Observable<ReviewJob> {
    return interval(3000).pipe(
      switchMap(() => this.getStatus(jobId)),
      takeWhile(
        (job) => job.status === 'queued' || job.status === 'running',
        true   // emit the terminal value too
      )
    );
  }
}
