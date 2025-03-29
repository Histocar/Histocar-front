CREATE TABLE IF NOT EXISTS "histocar_matricula_consultation" (
	"id" serial PRIMARY KEY NOT NULL,
	"matricula_id" integer NOT NULL,
	"consulted_by" varchar(255) NOT NULL,
	"consulted_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);
--> statement-breakpoint
DROP TABLE IF EXISTS "histocar_post";--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "histocar_matricula_consultation" ADD CONSTRAINT "histocar_matricula_consultation_matricula_id_histocar_matricula_id_fk" FOREIGN KEY ("matricula_id") REFERENCES "public"."histocar_matricula"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "histocar_matricula_consultation" ADD CONSTRAINT "histocar_matricula_consultation_consulted_by_histocar_user_id_fk" FOREIGN KEY ("consulted_by") REFERENCES "public"."histocar_user"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "matricula_consultation_matricula_id_idx" ON "histocar_matricula_consultation" USING btree ("matricula_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "matricula_consultation_user_id_idx" ON "histocar_matricula_consultation" USING btree ("consulted_by");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "unique_matricula_consultation_idx" ON "histocar_matricula_consultation" USING btree ("matricula_id","consulted_by");--> statement-breakpoint
ALTER TABLE "histocar_matricula" ADD CONSTRAINT "histocar_matricula_matricula_unique" UNIQUE("matricula");