import { IsNotEmpty, IsString } from 'class-validator';

export class SendLinksMessageDto {
  @IsString()
  @IsNotEmpty()
  links: string;
}
