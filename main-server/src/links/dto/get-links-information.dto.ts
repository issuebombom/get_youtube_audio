import { IsNotEmpty, IsString } from 'class-validator';

export class GetLinksInformationDto {
  @IsString()
  @IsNotEmpty()
  urls: string;
}
