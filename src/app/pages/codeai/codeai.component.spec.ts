import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CodeaiComponent } from './codeai.component';

describe('CodeaiComponent', () => {
  let component: CodeaiComponent;
  let fixture: ComponentFixture<CodeaiComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [CodeaiComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CodeaiComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
