import { ComponentFixture, TestBed } from '@angular/core/testing';

import { YatraGptComponent } from './yatra-gpt.component';

describe('YatraGptComponent', () => {
  let component: YatraGptComponent;
  let fixture: ComponentFixture<YatraGptComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [YatraGptComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(YatraGptComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
